import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { PantryItem, Category, ItemLog, PaginatedResponse } from '../models/models';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class PantryService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}


//pantry
  getItems(params: {
    household_id?: number;
    status?: string;
    category_id?: number;
    search?: string;
    expiring_soon?: boolean;
    ordering?: string;
  } = {}): Observable<PaginatedResponse<PantryItem>> {
    let httpParams = new HttpParams();
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== '') {
        httpParams = httpParams.set(k, String(v));
      }
    });
    return this.http.get<PaginatedResponse<PantryItem>>(
      `${this.apiUrl}/pantry-items/`, { params: httpParams }
    );
  }

  getItem(id: number): Observable<PantryItem> {
    return this.http.get<PantryItem>(`${this.apiUrl}/pantry-items/${id}/`);
  }

  createItem(data: Partial<PantryItem>): Observable<PantryItem> {
    return this.http.post<PantryItem>(`${this.apiUrl}/pantry-items/`, data);
  }

  updateItem(id: number, data: Partial<PantryItem>): Observable<PantryItem> {
    return this.http.patch<PantryItem>(`${this.apiUrl}/pantry-items/${id}/`, data);
  }

  deleteItem(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/pantry-items/${id}/`);
  }

  consumeItem(id: number, quantity: number): Observable<PantryItem> {
    return this.http.post<PantryItem>(`${this.apiUrl}/pantry-items/${id}/consume/`, { quantity });
  }

  wasteItem(id: number, quantity: number): Observable<PantryItem> {
    return this.http.post<PantryItem>(`${this.apiUrl}/pantry-items/${id}/waste/`, { quantity });
  }

  
  
//categories
  getCategories(): Observable<PaginatedResponse<Category>> {
    return this.http.get<PaginatedResponse<Category>>(`${this.apiUrl}/categories/`);
  }

  createCategory(data: { name: string;}): Observable<Category> {
    return this.http.post<Category>(`${this.apiUrl}/categories/`, data);
  }


//logs
  getLogs(householdId: number): Observable<PaginatedResponse<ItemLog>> {
    return this.http.get<PaginatedResponse<ItemLog>>(
      `${this.apiUrl}/logs/?household_id=${householdId}`
    );
  }
}
