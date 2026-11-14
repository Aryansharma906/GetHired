import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";

import { WorkspaceSearch } from "./workspace-search";

describe("workspace search", () => {
  it("opens by keyboard, filters real routes, and closes with Escape", async () => {
    const user = userEvent.setup();
    render(<WorkspaceSearch />);
    await user.keyboard("{Control>}k{/Control}");
    const input = screen.getByRole("searchbox", { name: "Search screens or applications" });
    expect(input).toHaveFocus();
    await user.type(input, "resume");
    expect(screen.getByRole("link", { name: "Base resume" })).toHaveAttribute("href", "/resume");
    expect(screen.queryByRole("link", { name: "Settings" })).not.toBeInTheDocument();
    await user.keyboard("{Escape}");
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("encodes Unicode and special characters in application search links", async () => {
    const user = userEvent.setup();
    render(<WorkspaceSearch />);
    await user.click(screen.getByRole("button", { name: "Search workspace" }));
    await user.type(screen.getByRole("searchbox"), "C++ & München");
    expect(screen.getByRole("link", { name: /Search applications for/ })).toHaveAttribute("href", "/applications?view=table&q=C%2B%2B%20%26%20M%C3%BCnchen");
  });
});
