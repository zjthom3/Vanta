import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { SessionProvider } from "next-auth/react";
import { vi } from "vitest";

import ApplicationsPage from "./page";

const getJsonMock = vi.fn();
const patchJsonMock = vi.fn().mockResolvedValue({});
const postFormDataMock = vi.fn().mockResolvedValue({});

vi.mock("@/lib/api-client", () => ({
  getJson: (...args: unknown[]) => getJsonMock(...args),
  patchJson: (...args: unknown[]) => patchJsonMock(...args),
  postFormData: (...args: unknown[]) => postFormDataMock(...args),
}));

describe("ApplicationsPage", () => {
  beforeEach(() => {
    getJsonMock.mockImplementation((path: string) => {
      if (path === "/applications/") {
        return Promise.resolve([
          {
            id: "app-1",
            title: "Product Designer",
            company: "Acme",
            stage: "prospect",
            url: "https://example.com/role",
            notes_count: 0,
            tasks: [],
          },
        ]);
      }
      if (path === "/applications/app-1/notes") {
        return Promise.resolve([]);
      }
      return Promise.resolve([]);
    });
  });

  it("renders kanban columns and supports note creation", async () => {
    const queryClient = new QueryClient();

    render(
      <SessionProvider session={{ user: { id: "user-1" }, expires: "" }}>
        <QueryClientProvider client={queryClient}>
          <ApplicationsPage />
        </QueryClientProvider>
      </SessionProvider>,
    );

    await screen.findByText(/Product Designer/i);
    expect(screen.getByText(/Prospect/i)).toBeInTheDocument();

    fireEvent.click(screen.getByText(/Product Designer/i));
    await screen.findByText(/Add note/i);

    const textarea = screen.getByPlaceholderText(/Next steps/i);
    fireEvent.change(textarea, { target: { value: "Reached out to hiring manager" } });
    fireEvent.submit(screen.getByText(/Save note/i).closest("form") as HTMLFormElement);

    await waitFor(() =>
      expect(postFormDataMock).toHaveBeenCalledWith(
        "/applications/app-1/notes",
        expect.any(FormData),
        { userId: "user-1" },
      ),
    );
  });
});
