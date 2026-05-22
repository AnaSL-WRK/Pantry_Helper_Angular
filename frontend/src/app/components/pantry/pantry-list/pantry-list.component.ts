import { Component, OnInit } from '@angular/core';
import { PantryService } from '../../../services/pantry.service';
import { HouseholdService } from '../../../services/household.service';
import { PantryItem, Category, Household } from '../../../models/models';

@Component({
  selector: 'app-pantry-list',
  templateUrl: './pantry-list.component.html',
  styleUrls: ['./pantry-list.component.css']
})


export class PantryListComponent implements OnInit {
  items: PantryItem[] = [];
  categories: Category[] = [];
  household: Household | null = null;
  loading = true;

  //filters
  searchTerm = '';
  statusFilter = '';
  categoryFilter = '';
  sortBy = 'name';
  showExpiringSoon = false;

  //modal state
  showForm = false;
  editItem: PantryItem | null = null;
  showConsumeModal = false;
  showWasteModal = false;
  actionItem: PantryItem | null = null;
  actionQty = 1;

  constructor(
    private pantryService: PantryService,
    private householdService: HouseholdService
  ) {}

  ngOnInit(): void {
    this.householdService.selectedHousehold$.subscribe(h => {
      this.household = h;
      if (h) this.load();
      else this.loading = false;
    });
    this.pantryService.getCategories().subscribe({
      next: res => { this.categories = res.results; }
    });
  }

  load(): void {
    if (!this.household) return;
    this.loading = true;
    this.pantryService.getItems({
      household_id: this.household.id,
      search: this.searchTerm,
      status: this.statusFilter,
      category_id: this.categoryFilter ? Number(this.categoryFilter) : undefined,
      ordering: this.sortBy,
      expiring_soon: this.showExpiringSoon || undefined,
    }).subscribe({
      next: res => { this.items = res.results; this.loading = false; },
      error: () => { this.loading = false; }
    });
  }

  onSearch(): void { this.load(); }
  onFilterChange(): void { this.load(); }

  openAdd(): void { this.editItem = null; this.showForm = true; }
  openEdit(item: PantryItem): void { this.editItem = item; this.showForm = true; }

  onFormSaved(): void {
    this.showForm = false;
    this.editItem = null;
    this.load();
  }

  openConsume(item: PantryItem): void {
    this.actionItem = item;
    this.actionQty = item.quantity;
    this.showConsumeModal = true;
  }

  openWaste(item: PantryItem): void {
    this.actionItem = item;
    this.actionQty = item.quantity;
    this.showWasteModal = true;
  }

  confirmConsume(): void {
    if (!this.actionItem) return;
    if (this.actionQty <= 0 || this.actionQty > this.actionItem.quantity) return;
    this.pantryService.consumeItem(this.actionItem.id, this.actionQty).subscribe({
      next: () => { this.showConsumeModal = false; this.load(); }
    });
  }

  confirmWaste(): void {
    if (!this.actionItem) return;
    if (this.actionQty <= 0 || this.actionQty > this.actionItem.quantity) return;
    this.pantryService.wasteItem(this.actionItem.id, this.actionQty).subscribe({
      next: () => { this.showWasteModal = false; this.load(); }
    });
  }

  deleteItem(item: PantryItem): void {
    if (!confirm('Delete "' + item.name + '"?')) return;
    this.pantryService.deleteItem(item.id).subscribe({
      next: () => this.load()
    });
  }

  getStatusClass(item: PantryItem): string {
    if (item.is_expired) return 'badge badge-danger';
    if (item.days_until_expiry !== null && item.days_until_expiry <= 3) return 'badge badge-warning';
    const map: Record<string, string> = {
      available: 'badge status-available',
      consumed: 'badge status-consumed',
      wasted: 'badge status-wasted',
    };
    return map[item.status] || 'badge badge-muted';
  }

  getExpiryLabel(item: PantryItem): string {
    if (!item.expiry_date) return '-';
    if (item.is_expired) return 'Expired';
    if (item.days_until_expiry === 0) return 'Today';
    if (item.days_until_expiry === 1) return 'Tomorrow';
    if (item.days_until_expiry !== null && item.days_until_expiry <= 7)
      return `${item.days_until_expiry}d`;
    return item.expiry_date.slice(0, 10);
  }

  canWrite(): boolean {
    const role = this.household?.current_user_role;
    return role === 'admin' || role === 'inventory_manager';
  }

  canConsume(): boolean {
    const role = this.household?.current_user_role;
    return role === 'admin' || role === 'inventory_manager' || role === 'member';
  }
}
