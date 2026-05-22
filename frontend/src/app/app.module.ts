import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule, HTTP_INTERCEPTORS } from '@angular/common/http';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { AuthInterceptor } from './services/auth.interceptor';

//components
import { NavComponent } from './components/nav/nav.component';
import { LoginComponent } from './components/auth/login/login.component';
import { RegisterComponent } from './components/auth/register/register.component';
import { ProfileComponent } from './components/auth/profile/profile.component';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { HouseholdListComponent } from './components/household/household-list/household-list.component';
import { HouseholdDetailComponent } from './components/household/household-detail/household-detail.component';
import { HouseholdFormComponent } from './components/household/household-form/household-form.component';
import { PantryListComponent } from './components/pantry/pantry-list/pantry-list.component';
import { PantryItemFormComponent } from './components/pantry/pantry-item-form/pantry-item-form.component';
import { RecipeListComponent } from './components/recipes/recipe-list/recipe-list.component';
import { RecipeDetailComponent } from './components/recipes/recipe-detail/recipe-detail.component';
import { RecipeFormComponent } from './components/recipes/recipe-form/recipe-form.component';

@NgModule({
  declarations: [
    AppComponent,
    NavComponent,
    LoginComponent,
    RegisterComponent,
    ProfileComponent,
    DashboardComponent,
    HouseholdListComponent,
    HouseholdDetailComponent,
    HouseholdFormComponent,
    PantryListComponent,
    PantryItemFormComponent,
    RecipeListComponent,
    RecipeDetailComponent,
    RecipeFormComponent,
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    FormsModule,
    ReactiveFormsModule,
  ],
  providers: [
    { provide: HTTP_INTERCEPTORS, useClass: AuthInterceptor, multi: true }
  ],
  bootstrap: [AppComponent]
})
export class AppModule {}
