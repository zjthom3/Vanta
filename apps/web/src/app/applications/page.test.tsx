import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { SessionProvider } from "next-auth/react";
import { vi } from "vitest";

import ApplicationsPage from "./page";

vi.mock("@/lib/api-client", () => ({
  getJson: vi.fn().mockResolvedValue([
    {
      id: "app-1",
      title: "Product Designer",
      company: "Acme",
      stage: "prospect",
      url: "https://example.com",
      tasks: [],
    },
  ]),
  patchJson: vi.fn().mockResolvedValue({}),
}));

const api = await import("@/lib/api-client");

describe("ApplicationsPage", () => {
  it("renders columns and updates stage", async () => {
    const queryClient = new QueryClient();

    render(
      <SessionProvider session={{ user: { id: "user-1" }, expires: "" }}>
        <QueryClientProvider client={queryClient}>
          <ApplicationsPage />
        </QueryClientProvider>
      </SessionProvider>
    );

    await screen.findByText(/Product Designer/i);
    const stageSelect = screen.getByDisplayValue(/Prospect/i) as HTMLSelectElement;
    fireEvent.change(stageSelect, { target: { value: "applied" } });

    await waitFor(() => expect(api.patchJson).toHaveBeenCalledWith("/applications/app-1", { stage: "applied" }, { userId: "user-1" }));
  });
});
