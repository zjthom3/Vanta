import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { SessionProvider } from "next-auth/react";
import { vi } from "vitest";

import ResumesPage from "./page";

vi.mock("@/lib/api-client", () => ({
  getJson: vi.fn().mockResolvedValue([
    { id: "resume-1", base: true, original_filename: "resume.pdf", created_at: new Date().toISOString(), ats_score: 70 },
  ]),
  postJson: vi.fn().mockResolvedValue({}),
}));

const api = await import("@/lib/api-client");

describe("ResumesPage", () => {
  it("lists resumes and triggers tailor", async () => {
    const queryClient = new QueryClient();

    render(
      <SessionProvider session={{ user: { id: "user-1" }, expires: "" }}>
        <QueryClientProvider client={queryClient}>
          <ResumesPage />
        </QueryClientProvider>
      </SessionProvider>
    );

    await screen.findByText(/resume.pdf/i);
    fireEvent.click(screen.getByRole("button", { name: /tailor/i }));
    await waitFor(() => expect(api.postJson).toHaveBeenCalled());
  });
});
