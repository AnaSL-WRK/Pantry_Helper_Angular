import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Recipe, PaginatedResponse } from '../models/models';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class RecipeService {
  private apiUrl = `${environment.apiUrl}/recipes`;

  constructor(private http: HttpClient) {}

  getAll(params: { search?: string; household_id?: number } = {}): Observable<PaginatedResponse<Recipe>> {
    let httpParams = new HttpParams();
    if (params.search) httpParams = httpParams.set('search', params.search);
    if (params.household_id) httpParams = httpParams.set('household_id', params.household_id);
    return this.http.get<PaginatedResponse<Recipe>>(this.apiUrl + '/', { params: httpParams });
  }

  get(id: number, householdId?: number): Observable<Recipe> {
    let params = new HttpParams();
    if (householdId) params = params.set('household_id', householdId);
    return this.http.get<Recipe>(`${this.apiUrl}/${id}/`, { params });
  }

  create(data: Partial<Recipe>): Observable<Recipe> {
    return this.http.post<Recipe>(this.apiUrl + '/', data);
  }

  update(id: number, data: Partial<Recipe>): Observable<Recipe> {
    return this.http.patch<Recipe>(`${this.apiUrl}/${id}/`, data);
  }

  delete(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}/`);
  }

  getSuggested(householdId: number): Observable<Recipe[]> {
    return this.http.get<Recipe[]>(`${this.apiUrl}/suggested/?household_id=${householdId}`);
  }
}
