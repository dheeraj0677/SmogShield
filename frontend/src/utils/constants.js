export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/+$/, '') || '';

export const POPULAR_CITIES = ['Delhi', 'Lahore', 'Lucknow', 'Beijing', 'London'];

export const HEALTH_CONDITION_OPTIONS = [
  { id: 'asthma', label: 'Asthma' },
  { id: 'copd', label: 'COPD' },
  { id: 'allergies', label: 'Allergies / Sinus' },
  { id: 'heart_disease', label: 'Heart Condition' },
];

export const COMMUTE_OPTIONS = [
  { value: 'car', label: 'Private Car' },
  { value: 'motorbike', label: 'Two-Wheeler / Bike' },
  { value: 'public_transit', label: 'Metro / Bus' },
  { value: 'walk_bike', label: 'Walk / Cycle' },
  { value: 'work_from_home', label: 'Work From Home' },
];

export const HOME_TYPE_OPTIONS = [
  { value: 'apartment', label: 'Apartment' },
  { value: 'independent_house', label: 'Independent House' },
  { value: 'shared_housing', label: 'Shared Housing' },
];

export const BUDGET_OPTIONS = [
  { value: 'low', label: 'Low / DIY Focus' },
  { value: 'medium', label: 'Moderate' },
  { value: 'high', label: 'Flexible' },
];

export const DEFAULT_USER_PROFILE = {
  city: 'Delhi',
  family_members: 3,
  has_children: true,
  has_elderly: false,
  health_conditions: ['asthma'],
  commute_type: 'car',
  home_type: 'apartment',
  has_air_purifier: false,
  budget: 'low',
  lifestyle_notes: '',
};

export const QUICK_CHAT_PROMPTS = [
  'How should I protect my family from winter smog today?',
  'Can I open windows or exercise outdoors right now?',
  'What low-cost DIY indoor air quality hacks work best?',
  'How much impact does switching my commute make today?',
];
