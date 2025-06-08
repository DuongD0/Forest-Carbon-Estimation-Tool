export interface Project {
    id: string;
    name: string;
    description: string | null;
    project_type: 'Forestry' | 'Renewable Energy';
    status: 'Draft' | 'Under Review' | 'Active' | 'Completed' | 'Rejected';
    owner_id: string;
    location_geometry: any; // Or a more specific GeoJSON type
    created_at: string;
    updated_at: string;
    ecosystem_id: string | null;
} 

export interface User {
    id: string;
    email: string;
    first_name: string | null;
    last_name: string | null;
    organization: string | null;
    is_active: boolean;
}

export interface CarbonCredit {
    id: string;
    project_id: string;
    vcs_serial_number: string;
    quantity_co2e: number;
    vintage_year: number;
    status: 'Issued' | 'Listed' | 'Sold' | 'Retired';
    issuance_date: string;
}

export interface P2PListing {
    id: string;
    credit_id: string;
    seller_id: string;
    price_per_ton: number;
    quantity: number;
    status: 'Active' | 'Sold' | 'Cancelled';
    created_at: string;
    credit?: CarbonCredit; // Optional, for eager loading
    seller?: User; // Optional, for eager loading
}

export interface Transaction {
    id: string;
    listing_id: string;
    buyer_id: string;
    seller_id: string;
    quantity: number;
    total_price: number;
    stripe_charge_id: string;
    status: 'Pending' | 'Completed' | 'Failed';
    created_at: string;
} 