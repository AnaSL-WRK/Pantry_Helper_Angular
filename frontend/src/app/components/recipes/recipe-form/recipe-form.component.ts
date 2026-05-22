import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { FormBuilder, FormGroup, FormArray, Validators } from '@angular/forms';
import { RecipeService } from '../../../services/recipe.service';
import { Recipe } from '../../../models/models';

@Component({
  selector: 'app-recipe-form',
  templateUrl: './recipe-form.component.html',
  styleUrls: ['./recipe-form.component.css']
})


export class RecipeFormComponent implements OnInit {
  @Input() recipe: Recipe | null = null;
  @Output() saved = new EventEmitter<void>();
  @Output() cancelled = new EventEmitter<void>();

  form: FormGroup;
  loading = false;
  error = '';

  units = ['units', 'g', 'kg', 'ml', 'l', 'tsp', 'tbsp', 'cup'];

  constructor(private fb: FormBuilder, private recipeService: RecipeService) {
    this.form = this.fb.group({
      name: ['', Validators.required],
      description: [''],
      instructions: ['', Validators.required],
      servings: [2, [Validators.required, Validators.min(1)]],
      prep_time_minutes: [30, [Validators.required, Validators.min(0)]],
      is_public: [true],
      ingredients: this.fb.array([])
    });
  }

  ngOnInit(): void {
    if (this.recipe) {
      this.form.patchValue({
        name: this.recipe.name,
        description: this.recipe.description,
        instructions: this.recipe.instructions,
        servings: this.recipe.servings,
        prep_time_minutes: this.recipe.prep_time_minutes,
        is_public: this.recipe.is_public,
      });
      this.recipe.ingredients.forEach(ing => this.addIngredient(ing));
    } else {
      this.addIngredient();
    }
  }

  get ingredients(): FormArray {
    return this.form.get('ingredients') as FormArray;
  }

  addIngredient(data?: { name: string; quantity: number; unit: string }): void {
    this.ingredients.push(this.fb.group({
      name: [data?.name || '', Validators.required],
      quantity: [data?.quantity || 1, [Validators.required, Validators.min(0.01)]],
      unit: [data?.unit || 'units', Validators.required],
    }));
  }

  removeIngredient(index: number): void {
    if (this.ingredients.length > 1) {
      this.ingredients.removeAt(index);
    }
  }

  submit(): void {
    if (this.form.invalid) return;
    this.loading = true;
    this.error = '';
    const data = this.form.value;

    const obs = this.recipe
      ? this.recipeService.update(this.recipe.id, data)
      : this.recipeService.create(data);

    obs.subscribe({
      next: () => { this.loading = false; this.saved.emit(); },
      error: (err) => {
        this.error = Object.values(err.error || {}).flat().join(' ') || 'Failed to save recipe.';
        this.loading = false;
      }
    });
  }
}
