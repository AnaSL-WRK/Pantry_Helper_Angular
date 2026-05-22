import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { HouseholdService } from '../../../services/household.service';
import { Household } from '../../../models/models';

@Component({
  selector: 'app-household-form',
  templateUrl: './household-form.component.html',
  styleUrls: ['./household-form.component.css']
})


export class HouseholdFormComponent implements OnInit {
  @Input() household: Household | null = null;
  @Output() saved = new EventEmitter<Household>();
  @Output() cancelled = new EventEmitter<void>();

  form: FormGroup;
  loading = false;
  error = '';

  constructor(private fb: FormBuilder, private householdService: HouseholdService) {
    this.form = this.fb.group({
      name: ['', Validators.required],
      description: ['']
    });
  }

  ngOnInit(): void {
    if (this.household) {
      this.form.patchValue(this.household);
    }
  }

  submit(): void {
    if (this.form.invalid) return;
    this.loading = true;
    this.error = '';
    const data = this.form.value;
    const obs = this.household
      ? this.householdService.update(this.household.id, data)
      : this.householdService.create(data);

    obs.subscribe({
      next: (h) => { this.loading = false; this.saved.emit(h); },
      error: (err) => {
        this.error = err.error?.name?.[0] || 'Failed to save household.';
        this.loading = false;
      }
    });
  }
}
