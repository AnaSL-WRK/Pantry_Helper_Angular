import { Component } from '@angular/core';
import { FormBuilder, FormGroup } from '@angular/forms';
import { AuthService } from '../../../services/auth.service';

@Component({
  selector: 'app-profile',
  templateUrl: './profile.component.html',
  styleUrls: ['./profile.component.css']
})


export class ProfileComponent {
  form: FormGroup;
  success = '';
  error = '';
  loading = false;

  constructor(private fb: FormBuilder, public authService: AuthService) {
    const u = authService.currentUser!;
    this.form = this.fb.group({
      first_name: [u.first_name],
      last_name: [u.last_name],
      email: [u.email],
      password: [''],
    });
  }

  submit(): void {
    this.loading = true;
    this.success = '';
    this.error = '';
    const data: any = { ...this.form.value };
    if (!data.password) delete data.password;
    this.authService.updateProfile(data).subscribe({
      next: () => {
        this.success = 'Profile updated successfully!';
        this.form.patchValue({ password: '' });
        this.loading = false;
      },
      error: () => {
        this.error = 'Update failed. Please try again.';
        this.loading = false;
      }
    });
  }
}
