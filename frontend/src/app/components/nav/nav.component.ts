import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { HouseholdService } from '../../services/household.service';
import { Household } from '../../models/models';

@Component({
  selector: 'app-nav',
  templateUrl: './nav.component.html',
  styleUrls: ['./nav.component.css']
})
export class NavComponent implements OnInit {
  households: Household[] = [];
  selectedHousehold: Household | null = null;

  constructor(
    public authService: AuthService,
    private householdService: HouseholdService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadHouseholds();
    this.householdService.selectedHousehold$.subscribe(h => {
      this.selectedHousehold = h;
    });
  }

  loadHouseholds(): void {
    this.householdService.getAll().subscribe({
      next: res => {
        this.households = res.results;
        if (!this.selectedHousehold && this.households.length > 0) {
          this.householdService.selectHousehold(this.households[0]);
        }
      }
    });
  }

  selectHousehold(h: Household): void {
    this.householdService.selectHousehold(h);
  }

  logout(): void {
    this.authService.logout().subscribe({
      next: () => this.router.navigate(['/']),
      error: () => {
        this.authService.clearSession();
        this.router.navigate(['/']);
      }
    });
  }
}
