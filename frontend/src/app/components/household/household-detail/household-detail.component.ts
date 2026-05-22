import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { HouseholdService } from '../../../services/household.service';
import { Household, HouseholdMember, ItemLog } from '../../../models/models';
import { PantryService } from '../../../services/pantry.service';
import { AuthService } from 'src/app/services/auth.service';

@Component({
  selector: 'app-household-detail',
  templateUrl: './household-detail.component.html',
  styleUrls: ['./household-detail.component.css']
})



export class HouseholdDetailComponent implements OnInit {
  household: Household | null = null;
  logs: ItemLog[] = [];
  loading = true;
  showEditForm = false;
  showAddMember = false;
  addMemberForm: FormGroup;
  addMemberError = '';
  addMemberLoading = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private householdService: HouseholdService,
    private pantryService: PantryService,
    private authService: AuthService,
    private fb: FormBuilder
  ) {
    this.addMemberForm = this.fb.group({
      username: ['', Validators.required],
      role: ['member', Validators.required]
    });
  }

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    this.householdService.get(id).subscribe({
      next: h => { this.household = h; this.loading = false; this.loadLogs(id); },
      error: () => { this.router.navigate(['/households']); }
    });
  }

  loadLogs(id: number): void {
    this.pantryService.getLogs(id).subscribe({
      next: res => { this.logs = res.results.slice(0, 10); }
    });
  }

  onFormSaved(h: Household): void {
    this.household = h;
    this.showEditForm = false;
  }

  removeMember(member: HouseholdMember): void {
    if (!this.household) return;
    if (!confirm('Remove ' + member.user.username + ' from this household?')) return;
    this.householdService.removeMember(this.household.id, member.id).subscribe({
      next: () => {
        this.household!.members = this.household!.members.filter(m => m.id !== member.id);
      }
    });
  }

  changeRole(member: HouseholdMember, role: string): void {
    if (!this.household) return;
    this.householdService.updateMember(this.household.id, member.id, role).subscribe({
      next: (updated) => {
        const idx = this.household!.members.findIndex(m => m.id === member.id);
        if (idx !== -1) this.household!.members[idx] = updated;
      }
    });
  }

  addMember(): void {
    if (this.addMemberForm.invalid || !this.household) return;
    this.addMemberLoading = true;
    this.addMemberError = '';
    const { username, role } = this.addMemberForm.value;
 
    //username to user id
    this.authService.searchUser(username).subscribe({
      
      next: (user: any) => {
        //add member using id
        this.householdService.addMember(this.household!.id, { user_id: user.id, role }).subscribe({
          next: (member) => {
            this.household!.members.push(member);
            this.showAddMember = false;
            this.addMemberForm.reset({ role: 'member' });
            this.addMemberLoading = false;
          },
          error: (err) => {
            this.addMemberError = err.error?.error || err.error?.non_field_errors?.[0] || 'Failed to add member.';
            this.addMemberLoading = false;
          }
        });
      },
      error: (err) => {
        this.addMemberError = err.error?.error || 'User "' + username + '" not found.';
        this.addMemberLoading = false;
      }
    });
  }
 

  isAdmin(): boolean {
    return this.household?.current_user_role === 'admin';
  }

  getRoleBadge(role: string): string {
    const map: Record<string, string> = {
      admin: 'badge badge-success',
      inventory_manager: 'badge badge-info',
      member: 'badge badge-muted',
      viewer: 'badge badge-muted',
    };
    return map[role] || 'badge badge-muted';
  }

}
