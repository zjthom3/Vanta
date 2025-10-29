import { describe, expect, it } from "vitest";

import { useOnboardingStore } from "./onboarding";

describe("useOnboardingStore", () => {
  it("updates individual fields", () => {
    const store = useOnboardingStore.getState();
    useOnboardingStore.getState().updateField("fullName", "Ada");
    expect(useOnboardingStore.getState().fullName).toBe("Ada");

    useOnboardingStore.getState().updateField("targetLocations", ["Remote"]);
    expect(useOnboardingStore.getState().targetLocations).toEqual(["Remote"]);

    useOnboardingStore.getState().updateField("scheduleCron", "0 6 * * *");
    expect(useOnboardingStore.getState().scheduleCron).toBe("0 6 * * *");

    // cleanup
    store.reset();
  });
});
