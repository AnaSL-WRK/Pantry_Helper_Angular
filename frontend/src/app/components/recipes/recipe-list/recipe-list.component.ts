import { Component, OnInit } from '@angular/core';
import { RecipeService } from '../../../services/recipe.service';
import { HouseholdService } from '../../../services/household.service';
import { Recipe, Household } from '../../../models/models';

@Component({
  selector: 'app-recipe-list',
  templateUrl: './recipe-list.component.html',
  styleUrls: ['./recipe-list.component.css']
})


export class RecipeListComponent implements OnInit {
  recipes: Recipe[] = [];
  suggestedRecipes: Recipe[] = [];
  household: Household | null = null;
  loading = true;
  loadingSuggested = false;
  searchTerm = '';
  showSuggested = false;
  showForm = false;
  editRecipe: Recipe | null = null;

  constructor(
    private recipeService: RecipeService,
    private householdService: HouseholdService
  ) {}

  ngOnInit(): void {
    this.householdService.selectedHousehold$.subscribe(h => {
      this.household = h;
      this.load();
    });
  }

  load(): void {
    this.loading = true;
    const params: any = { search: this.searchTerm };
    if (this.household) params.household_id = this.household.id;
    this.recipeService.getAll(params).subscribe({
      next: res => { this.recipes = res.results; this.loading = false; },
      error: () => { this.loading = false; }
    });
  }

  loadSuggested(): void {
    if (!this.household) return;
    this.loadingSuggested = true;
    this.showSuggested = true;
    this.recipeService.getSuggested(this.household.id).subscribe({
      next: recipes => { this.suggestedRecipes = recipes; this.loadingSuggested = false; },
      error: () => { this.loadingSuggested = false; }
    });
  }

  onSearch(): void { this.load(); }

  openAdd(): void { this.editRecipe = null; this.showForm = true; }
  openEdit(recipe: Recipe, e: Event): void {
    e.stopPropagation();
    this.editRecipe = recipe;
    this.showForm = true;
  }

  onFormSaved(): void {
    this.showForm = false;
    this.editRecipe = null;
    this.load();
  }

  deleteRecipe(recipe: Recipe, e: Event): void {
    e.stopPropagation();
    if (!confirm('Delete recipe "' + recipe.name + '"?')) return;
    this.recipeService.delete(recipe.id).subscribe({ next: () => this.load() });
  }

  isOwner(recipe: Recipe): boolean {
    return true;
  }

  getIngredientPreview(recipe: Recipe): string {
    return recipe.ingredients.slice(0, 3).map(i => i.name).join(', ');
  }

  hasMoreIngredients(recipe: Recipe): boolean {
    return recipe.ingredients.length > 3;
  }

  extraIngredientCount(recipe: Recipe): number {
    return recipe.ingredients.length - 3;
  }
}