export interface Lead {
  id: number;

  business_name: string;
  contact_person: string;
  email: string;
  phone: string;
  website: string;

  city: string;
  category: string;

  source: string;
  notes: string;

  status: string;
  pipeline_stage: string;

  estimated_value: number;

  last_contacted: string | null;
  next_followup: string | null;

  created_at: string;
}
