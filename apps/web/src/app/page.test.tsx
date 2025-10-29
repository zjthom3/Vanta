import { render, screen } from "@testing-library/react";
import HomePage from "./page";

describe("HomePage", () => {
  it("renders welcome copy", async () => {
    const page = await HomePage();
    render(page);
    expect(screen.getByText(/Welcome to Vanta/i)).toBeInTheDocument();
  });
});
