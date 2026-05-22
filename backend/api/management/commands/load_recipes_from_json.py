import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from api.models import Category, Recipe, RecipeIngredient


class Command(BaseCommand):
    help = "Load preloaded recipes from a JSON file into Recipe and RecipeIngredient."

    def add_arguments(self, parser):
        parser.add_argument(
            "json_path",
            nargs="?",
            default="api/fixtures/wasteless_recipes_500.json",
            help="Path to the recipes JSON file (relative to manage.py).",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing preloaded recipes before loading.",
        )

    def handle(self, *args, **options):
        json_path = Path(options["json_path"])

        if not json_path.exists():
            raise CommandError(f"File not found: {json_path}")

        with json_path.open("r", encoding="utf-8") as fh:
            payload = json.load(fh)

        recipes_data = payload.get("recipes")
        if not isinstance(recipes_data, list):
            raise CommandError('JSON must contain a top-level "recipes" list.')

        if options["clear"]:
            preloaded = Recipe.objects.filter(is_preloaded=True)
            RecipeIngredient.objects.filter(recipe__in=preloaded).delete()
            deleted_count, _ = preloaded.delete()
            self.stdout.write(self.style.WARNING(f"Deleted {deleted_count} preloaded recipes."))

        #cache categories: avoid DB hits
        category_cache = {c.name.casefold(): c for c in Category.objects.all()}

        created = 0
        updated = 0

        for recipe_data in recipes_data:
            name = str(recipe_data.get("name", "")).strip()
            if not name:
                continue

            source_url  = str(recipe_data.get("source_url", "") or "").strip()
            source_site = str(recipe_data.get("source_site", "") or "").strip()
            author      = str(recipe_data.get("author", "") or "").strip()
            description = str(recipe_data.get("description", "") or "").strip()

            #build instructions string from steps list
            steps_data = recipe_data.get("steps", [])
            sorted_steps = sorted(steps_data, key=lambda s: s.get("position", 0))
            instructions_lines = [
                f"{i + 1}. {str(s.get('instruction', '')).strip()}"
                for i, s in enumerate(sorted_steps)
                if str(s.get("instruction", "")).strip()
            ]
            instructions = "\n".join(instructions_lines) or "See source for instructions."

            #find or create
            recipe = None
            if source_url:
                recipe = Recipe.objects.filter(source_url=source_url, is_preloaded=True).first()
            if recipe is None:
                recipe = Recipe.objects.filter(name=name, is_preloaded=True).first()

            if recipe is None:
                recipe = Recipe.objects.create(
                    name=name,
                    description=description,
                    instructions=instructions,
                    author=author,
                    source_url=source_url,
                    source_site=source_site,
                    is_preloaded=True,
                    is_public=True,
                    created_by=None,
                )
                created += 1
            else:
                recipe.name         = name
                recipe.description  = description
                recipe.instructions = instructions
                recipe.author       = author
                recipe.source_url   = source_url
                recipe.source_site  = source_site
                recipe.save()

                recipe.ingredients.all().delete()
                updated += 1

            ingredients_data = sorted(
                recipe_data.get("ingredients", []),
                key=lambda x: x.get("position", 0)
            )

            for ing in ingredients_data:
                ing_name = str(ing.get("item_name", "")).strip()
                if not ing_name:
                    continue

                category_name = str(ing.get("category", "") or "").strip()
                category = None
                if category_name:
                    key = category_name.casefold()
                    category = category_cache.get(key)
                    if category is None:
                        category, _ = Category.objects.get_or_create(name=category_name)
                        category_cache[key] = category

                raw_qty = ing.get("quantity")
                try:
                    quantity = float(raw_qty) if raw_qty is not None else 1.0
                except (TypeError, ValueError):
                    quantity = 1.0

                unit = str(ing.get("unit") or "units").strip() or "units"

                RecipeIngredient.objects.create(
                    recipe=recipe,
                    name=ing_name,
                    quantity=quantity,
                    unit=unit,
                )

        self.stdout.write(self.style.SUCCESS(
            f"Done. Recipes created={created}, updated={updated}."
        ))
