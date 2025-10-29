import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen } from "@testing-library/react";
import { SessionProvider } from "next-auth/react";

import OnboardingPage from "./page";

describe("OnboardingPage", () => {
  it("renders the four-step wizard heading", () => {
    const queryClient = new QueryClient();

    render(
      <SessionProvider session={null}>
        <QueryClientProvider client={queryClient}>
          <OnboardingPage />
        </QueryClientProvider>
      </SessionProvider>
    );

    expect(screen.getByText(/Get set up in four quick steps/i)).toBeInTheDocument();
  });
});
