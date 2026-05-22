import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { HouseholdService } from '../../services/household.service';
import { PantryService } from '../../services/pantry.service';
import { RecipeService } from '../../services/recipe.service';
import { Household, HouseholdStats, PantryItem, Recipe } from '../../models/models';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})


export class DashboardComponent implements OnInit {
  household: Household | null = null;
  stats: HouseholdStats | null = null;
  expiringItems: PantryItem[] = [];
  suggestedRecipes: Recipe[] = [];
  loading = true;

  constructor(
    public authService: AuthService,
    private householdService: HouseholdService,
    private pantryService: PantryService,
    private recipeService: RecipeService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.householdService.selectedHousehold$.subscribe(h => {
      this.household = h;
      if (h) {
        this.loadData(h.id);
      } else {
        this.loading = false;
      }
    });
  }

  loadData(householdId: number): void {
    this.loading = true;
    this.householdService.getStats(householdId).subscribe({
      next: stats => { this.stats = stats; },
      error: () => {}
    });
    this.pantryService.getItems({ household_id: householdId, expiring_soon: true }).subscribe({
      next: res => { this.expiringItems = res.results.slice(0, 5); },
      error: () => {}
    });
    this.recipeService.getSuggested(householdId).subscribe({
      next: recipes => {
        this.suggestedRecipes = recipes.slice(0, 3);
        this.loading = false;
      },
      error: () => { this.loading = false; }
    });
  }

  getDaysLabel(days: number | null): string {
    if (days === null) return '';
    if (days < 0) return 'Expired';
    if (days === 0) return 'Today';
    if (days === 1) return 'Tomorrow';
    return 'In ' + days + ' days';
  }

  getDaysBadge(days: number | null): string {
    if (days === null) return '';
    if (days < 0) return 'badge badge-danger';
    if (days <= 2) return 'badge badge-danger';
    if (days <= 7) return 'badge badge-warning';
    return 'badge badge-success';
  }
}
