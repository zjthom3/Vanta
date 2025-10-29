import "@testing-library/jest-dom/vitest";

import { vi } from "vitest";

vi.mock("@/auth", () => ({
  auth: vi.fn().mockResolvedValue(null),
}));
