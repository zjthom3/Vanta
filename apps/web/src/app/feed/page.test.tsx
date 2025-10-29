import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { SessionProvider } from "next-auth/react";
import { vi } from "vitest";

import FeedPage from "./page";

vi.mock("@/lib/api-client", () => ({
  getJson: vi.fn().mockResolvedValue({
    items: [
      {
        id: "1",
        title: "Engineer",
        company: "Acme",
        location: "Remote",
        remote: true,
        url: "https://example.com",
        tags: ["Engineering"],
      },
    ],
    page: 1,
    limit: 20,
    total: 1,
  }),
  postJson: vi.fn().mockResolvedValue({ status: "hidden" }),
}));

const apiClient = await import("@/lib/api-client");
const postJsonMock = vi.mocked(apiClient.postJson);

describe("FeedPage", () => {
  it("renders job cards and allows hide", async () => {
    const queryClient = new QueryClient();
    render(
      <SessionProvider session={{ user: { id: "user-1" }, expires: "" }}>
        <QueryClientProvider client={queryClient}>
          <FeedPage />
        </QueryClientProvider>
      </SessionProvider>
    );

    await screen.findByRole("heading", { name: /Engineer/i });
    expect(screen.getByText(/Acme/i)).toBeInTheDocument();

    const hideButton = screen.getByRole("button", { name: /hide/i });
    fireEvent.click(hideButton);
    await waitFor(() => expect(postJsonMock).toHaveBeenCalled());
    expect(postJsonMock).toHaveBeenCalledWith("/feed/jobs/1/hide", {}, { userId: "user-1" });
  });
});
