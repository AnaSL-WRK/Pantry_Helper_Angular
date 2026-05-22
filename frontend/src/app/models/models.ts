export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
}

export interface AuthResponse {
  token: string;
  user: User;
}

export interface Household {
  id: number;
  name: string;
  description: string;
  created_by: User;
  created_at: string;
  members: HouseholdMember[];
  member_count: number;
  current_user_role: string | null;
}

export interface HouseholdMember {
  id: number;
  user: User;
  role: string;
  joined_at: string;
}

export interface Category {
  id: number;
  name: string;
}

export interface PantryItem {
  id: number;
  household: number;
  name: string;
  category: Category | null;
  category_id?: number | null;
  quantity: number;
  unit: string;
  expiry_date: string | null;
  status: 'available' | 'low' | 'consumed' | 'wasted';
  notes: string;
  added_by: User | null;
  added_at: string;
  updated_at: string;
  is_expired: boolean;
  days_until_expiry: number | null;
}
 
export interface RecipeIngredient {
  id?: number;
  name: string;
  quantity: number;
  unit: string;
}
 
export interface Recipe {
  id: number;
  name: string;
  description: string;
  instructions: string;
  servings: number;
  prep_time_minutes: number;
  created_by: User | null;
  is_public: boolean;
  created_at: string;
  ingredients: RecipeIngredient[];
  can_make: boolean | null;
}
 
export interface ItemLog {
  id: number;
  item_name: string;
  user: User | null;
  action: string;
  quantity_change: number | null;
  timestamp: string;
  notes: string;
}
 
export interface HouseholdStats {
  total_items: number;
  expiring_soon: number;
  expired: number;
  wasted: number;
  consumed: number;
  categories: number;
}
 
export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
 