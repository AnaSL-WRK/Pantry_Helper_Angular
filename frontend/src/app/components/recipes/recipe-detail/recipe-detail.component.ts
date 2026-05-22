import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { RecipeService } from '../../../services/recipe.service';
import { HouseholdService } from '../../../services/household.service';
import { AuthService } from '../../../services/auth.service';
import { Recipe } from '../../../models/models';

@Component({
  selector: 'app-recipe-detail',
  templateUrl: './recipe-detail.component.html',
  styleUrls: ['./recipe-detail.component.css']
})


export class RecipeDetailComponent implements OnInit {
  recipe: Recipe | null = null;
  loading = true;
  showEditForm = false;
  householdId: number | null = null;
  householdRole: string | null = null;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private recipeService: RecipeService,
    private householdService: HouseholdService,
    public authService: AuthService
  ) {}

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    this.householdService.selectedHousehold$.subscribe(h => {
      this.householdId = h?.id ?? null;
      this.householdRole = h?.current_user_role ?? null;
      this.loadRecipe(id);
    });
  }

  loadRecipe(id: number): void {
    this.loading = true;
    this.recipeService.get(id, this.householdId ?? undefined).subscribe({
      next: recipe => { this.recipe = recipe; this.loading = false; },
      error: () => { this.router.navigate(['/recipes']); }
    });
  }

  onFormSaved(): void {
    this.showEditForm = false;
    const id = Number(this.route.snapshot.paramMap.get('id'));
    this.recipeService.get(id, this.householdId ?? undefined).subscribe({ next: r => this.recipe = r });
  }

  delete(): void {
    if (!this.recipe || !confirm('Delete "' + this.recipe.name + '"?')) return;
    this.recipeService.delete(this.recipe.id).subscribe({
      next: () => this.router.navigate(['/recipes'])
    });
  }

  isIngredientAvailable(name: string): boolean {
    return (this.recipe?.available_ingredient_names ?? []).includes(name.toLowerCase());
  }

  isOwner(): boolean {
    if (!this.recipe || this.recipe.is_preloaded) return false;
    const currentUser = this.authService.currentUser;
    if (!currentUser) return false;
    if (this.recipe.created_by?.id === currentUser.id) return true;
    return this.householdRole === 'admin';
  }

  formatInstructions(text: string): string[] {
    return text.split('\n')
      .map(l => l.trim())
      .filter(l => l.length > 0)
      .map(l => l.replace(/^\d+\.\s*/, ''));
  }
}