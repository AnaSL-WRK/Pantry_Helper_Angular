import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { Household, HouseholdMember, HouseholdStats, PaginatedResponse } from '../models/models';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class HouseholdService {
  private apiUrl = `${environment.apiUrl}/households`;
  private selectedHouseholdSubject = new BehaviorSubject<Household | null>(null);
  selectedHousehold$ = this.selectedHouseholdSubject.asObservable();

  constructor(private http: HttpClient) {}

  get selectedHousehold(): Household | null {
    return this.selectedHouseholdSubject.value;
  }

  selectHousehold(h: Household | null): void {
    this.selectedHouseholdSubject.next(h);
  }

  getAll(): Observable<PaginatedResponse<Household>> {
    return this.http.get<PaginatedResponse<Household>>(this.apiUrl + '/');
  }

//household crud
  get(id: number): Observable<Household> {
    return this.http.get<Household>(`${this.apiUrl}/${id}/`);
  }

  create(data: { name: string; description: string }): Observable<Household> {
    return this.http.post<Household>(this.apiUrl + '/', data);
  }

  update(id: number, data: Partial<Household>): Observable<Household> {
    return this.http.patch<Household>(`${this.apiUrl}/${id}/`, data);
  }

  delete(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}/`);
  }

  
//members and stats
  getMembers(id: number): Observable<HouseholdMember[]> {
    return this.http.get<HouseholdMember[]>(`${this.apiUrl}/${id}/members/`);
  }

  addMember(householdId: number, data: { user_id: number; role: string }): Observable<HouseholdMember> {
    return this.http.post<HouseholdMember>(`${this.apiUrl}/${householdId}/members/`, data);
  }

  updateMember(householdId: number, memberId: number, role: string): Observable<HouseholdMember> {
    return this.http.patch<HouseholdMember>(
      `${this.apiUrl}/${householdId}/members/${memberId}/`, { role }
    );
  }

  removeMember(householdId: number, memberId: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${householdId}/members/${memberId}/`);
  }

  getStats(id: number): Observable<HouseholdStats> {
    return this.http.get<HouseholdStats>(`${this.apiUrl}/${id}/stats/`);
  }
}
