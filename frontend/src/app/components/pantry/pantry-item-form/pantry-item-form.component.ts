import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { PantryService } from '../../../services/pantry.service';
import { PantryItem, Category, Household } from '../../../models/models';

@Component({
  selector: 'app-pantry-item-form',
  templateUrl: './pantry-item-form.component.html',
  styleUrls: ['./pantry-item-form.component.css']
})


export class PantryItemFormComponent implements OnInit {
  @Input() household!: Household;
  @Input() item: PantryItem | null = null;
  @Input() categories: Category[] = [];
  @Output() saved = new EventEmitter<void>();
  @Output() cancelled = new EventEmitter<void>();

  form: FormGroup;
  loading = false;
  error = '';

  units = ['units', 'g', 'kg', 'ml', 'l', 'tsp', 'tbsp', 'cup'];
  statuses = ['available', 'low', 'consumed', 'wasted'];

  constructor(private fb: FormBuilder, private pantryService: PantryService) {
    this.form = this.fb.group({
      name: ['', Validators.required],
      category_id: [null],
      quantity: [1, [Validators.required, Validators.min(0)]],
      unit: ['units', Validators.required],
      expiry_date: [null],
      status: ['available', Validators.required],
      notes: ['']
    });
  }

  ngOnInit(): void {
    if (this.item) {
      this.form.patchValue({
        ...this.item,
        category_id: this.item.category?.id ?? null,
      });
    }
  }

  submit(): void {
    if (this.form.invalid) return;
    this.loading = true;
    this.error = '';
    const data: any = { ...this.form.value, household: this.household.id };
    if (!data.expiry_date) delete data.expiry_date;
    if (!data.category_id) data.category_id = null;

    const obs = this.item
      ? this.pantryService.updateItem(this.item.id, data)
      : this.pantryService.createItem(data);

    obs.subscribe({
      next: () => { this.loading = false; this.saved.emit(); },
      error: (err) => {
        const errors = err.error;
        if (errors) {
          this.error = Object.entries(errors).map(([k, v]) => `${k}: ${(v as string[]).join(', ')}`).join(' | ');
        } else {
          this.error = 'Failed to save item.';
        }
        this.loading = false;
      }
    });
  }
}
