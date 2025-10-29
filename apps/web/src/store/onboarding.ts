"use client";

import { create } from "zustand";

export type OnboardingFormState = {
  fullName: string;
  email: string;
  primaryRole: string;
  targetLocations: string[];
  yearsExperience: number;
  resumeFile: File | null;
  scheduleCron: string;
  timezone: string;
};

const initialState: OnboardingFormState = {
  fullName: "",
  email: "",
  primaryRole: "",
  targetLocations: [],
  yearsExperience: 0,
  resumeFile: null,
  scheduleCron: "0 5 * * *",
  timezone: "UTC",
};

export type OnboardingActions = {
  updateField: <K extends keyof OnboardingFormState>(key: K, value: OnboardingFormState[K]) => void;
  reset: () => void;
};

export const useOnboardingStore = create<OnboardingFormState & OnboardingActions>((set) => ({
  ...initialState,
  updateField: (key, value) => set(() => ({ [key]: value } as Partial<OnboardingFormState>)),
  reset: () => set(() => ({ ...initialState })),
}));
