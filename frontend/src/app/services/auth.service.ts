import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { User, AuthResponse } from '../models/models';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private apiUrl = environment.apiUrl;
  private currentUserSubject = new BehaviorSubject<User | null>(this.loadUser());
  currentUser$ = this.currentUserSubject.asObservable();

  constructor(private http: HttpClient) {}

  private loadUser(): User | null {
    const u = localStorage.getItem('user');
    return u ? JSON.parse(u) : null;
  }

  get currentUser(): User | null {
    return this.currentUserSubject.value;
  }

  get token(): string | null {
    return localStorage.getItem('token');
  }

  get isLoggedIn(): boolean {
    return !!this.token;  //converts token to boolean, true if exists, false if null
  }

  register(data: { username: string; email: string; password: string; first_name?: string; last_name?: string }): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${this.apiUrl}/auth/register/`, data).pipe(
      tap(res => this.saveSession(res))
    );
  }

  login(username: string, password: string): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${this.apiUrl}/auth/login/`, { username, password }).pipe(
      tap(res => this.saveSession(res))
    );
  }

  logout(): Observable<any> {
    return this.http.post(`${this.apiUrl}/auth/logout/`, {}).pipe(
      tap(() => this.clearSession())
    );
  }

  updateProfile(data: Partial<User & { password?: string }>): Observable<User> {
    return this.http.patch<User>(`${this.apiUrl}/auth/profile/`, data).pipe(
      tap(user => {
        localStorage.setItem('user', JSON.stringify(user));
        this.currentUserSubject.next(user);
      })
    );
  }

  private saveSession(res: AuthResponse): void {
    localStorage.setItem('token', res.token);
    localStorage.setItem('user', JSON.stringify(res.user));
    this.currentUserSubject.next(res.user);
  }

  clearSession(): void {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    this.currentUserSubject.next(null);
  }

  searchUser(username: string): Observable<any> {
    return this.http.get(`${this.apiUrl}/auth/search-user/?username=${encodeURIComponent(username)}`);
  }
}
