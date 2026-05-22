import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { AuthGuard, GuestGuard } from './guards/auth.guard';

import { LoginComponent } from './components/auth/login/login.component';
import { RegisterComponent } from './components/auth/register/register.component';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { HouseholdListComponent } from './components/household/household-list/household-list.component';
import { HouseholdDetailComponent } from './components/household/household-detail/household-detail.component';
import { PantryListComponent } from './components/pantry/pantry-list/pantry-list.component';
import { RecipeListComponent } from './components/recipes/recipe-list/recipe-list.component';
import { RecipeDetailComponent } from './components/recipes/recipe-detail/recipe-detail.component';
import { ProfileComponent } from './components/auth/profile/profile.component';

const routes: Routes = [
  { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
  { path: '**', redirectTo: 'dashboard' },
  { path: 'login', component: LoginComponent, canActivate: [GuestGuard] },
  { path: 'register', component: RegisterComponent, canActivate: [GuestGuard] },

  { path: 'dashboard', component: DashboardComponent, canActivate: [AuthGuard] },
  { path: 'households', component: HouseholdListComponent, canActivate: [AuthGuard] },
  { path: 'households/:id', component: HouseholdDetailComponent, canActivate: [AuthGuard] },

  { path: 'pantry', component: PantryListComponent, canActivate: [AuthGuard] },
  { path: 'recipes', component: RecipeListComponent, canActivate: [AuthGuard] },
  { path: 'recipes/:id', component: RecipeDetailComponent, canActivate: [AuthGuard] },

  { path: 'profile', component: ProfileComponent, canActivate: [AuthGuard] },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {}
