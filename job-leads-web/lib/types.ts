export type Job = {
  id: string;
  title: string;
  company: string;
  location: string;
  salary?: string;
  tags?: string;
  posted_at?: string;
  url: string;
  source: string;
  collected_at?: string;
  description?: string;
  lead?: Lead;
};

export type Lead = {
  id: string;
  status: string;
  score: number;
  favourite: boolean;
  resume_url?: string;
  cover_letter_url?: string;
  next_action?: string;
  next_action_date?: string;
  notes?: string;
  updated_at?: string;
};

export type Filters = {
  q?: string;
  source?: string;
  location?: string;
  status?: string;
};

