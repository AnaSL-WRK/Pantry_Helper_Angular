import { Component, OnInit } from '@angular/core';
import { HouseholdService } from '../../../services/household.service';
import { Household } from '../../../models/models';

@Component({
  selector: 'app-household-list',
  templateUrl: './household-list.component.html',
  styleUrls: ['./household-list.component.css']
})


export class HouseholdListComponent implements OnInit {
  households: Household[] = [];
  loading = true;
  showForm = false;
  selectedHousehold: Household | null = null;

  constructor(private householdService: HouseholdService) {}

  ngOnInit(): void {
    this.load();
    this.householdService.selectedHousehold$.subscribe(h => {
      this.selectedHousehold = h;
    });
  }

  load(): void {
    this.householdService.getAll().subscribe({
      next: res => { this.households = res.results; this.loading = false; },
      error: () => { this.loading = false; }
    });
  }

  onFormSaved(): void {
    this.showForm = false;
    this.load();
  }

  select(h: Household): void {
    this.householdService.selectHousehold(h);
  }

  delete(h: Household): void {
    if (!confirm('Delete "' + h.name + '"? This cannot be undone.')) return;
    this.householdService.delete(h.id).subscribe({
      next: () => {
        if (this.selectedHousehold?.id === h.id) {
          this.householdService.selectHousehold(null);
        }
        this.load();
      }
    });
  }

  getRoleBadge(role: string | null): string {
    const map: Record<string, string> = {
      admin: 'badge badge-success',
      inventory_manager: 'badge badge-info',
      member: 'badge badge-muted',
      viewer: 'badge badge-muted',
    };
    return role ? map[role] || 'badge badge-muted' : '';
  }
}
