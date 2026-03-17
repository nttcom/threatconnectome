import { addHours } from "date-fns";
import type { Meta, StoryObj } from "@storybook/react-vite";

import { InvitationManageDialog } from "./InvitationManageDialog";

const meta = {
  component: InvitationManageDialog,
  tags: ["autodocs"],
  parameters: {
    docs: {
      description: {
        component: `
A dialog component for issuing and managing invitation links to a team.

**Key features:**
- List of issued invitation links (showing active/expired status)
- Create new invitation links (with usage limit and expiration settings)
- Copy and revoke links

**Screen flow:**
\`List\` → \`Create form\` → \`Created\` → \`List\`
        `,
      },
    },
  },
  argTypes: {
    initialInvitations: {
      description: "List of invitation links to display initially (for mocking)",
      control: false,
    },
  },
  args: {},
} satisfies Meta<typeof InvitationManageDialog>;

export default meta;
type Story = StoryObj<typeof meta>;

/**
 * Normal state with a mix of active and expired links.
 * Shows the difference in status badge color/text and the behavior of copy/revoke buttons.
 */
export const ListWithInvitations: Story = {
  name: "List: Normal (multiple links)",
  args: {
    initialInvitations: [
      {
        id: "1",
        link: "https://example.com/pteam/join?token=xt7k9p2m",
        limitCount: null,
        expiration: null,
        usedCount: 0,
      },
      {
        id: "2",
        link: "https://example.com/pteam/join?token=b4v9m1zq",
        limitCount: 5,
        expiration: addHours(new Date(), 24),
        usedCount: 2,
      },
    ],
  },
  parameters: {
    docs: {
      description: {
        story:
          "State with 2 active links. An unlimited/no-expiration link and a usage-limited/expiring link are shown side by side. The 'Revoke' button removes a link from the list.",
      },
    },
  },
};

/**
 * State with no issued links.
 * Verifies that the empty state message is displayed.
 */
export const ListEmpty: Story = {
  name: "List: Empty (0 links)",
  args: {
    initialInvitations: [],
  },
  parameters: {
    docs: {
      description: {
        story:
          "Initial state with no invitation links. A message saying 'No active invitation links' is displayed. The 'Create New' button navigates to the creation form.",
      },
    },
  },
};

/**
 * For verifying scrolling behavior when a large number of links exist.
 * Checks that no layout breakage occurs.
 */
export const ListManyInvitations: Story = {
  name: "List: Many links (8 items)",
  args: {
    initialInvitations: Array.from({ length: 8 }, (_, i) => ({
      id: String(i + 1),
      link: `https://example.com/pteam/join?token=token${String(i + 1).padStart(4, "0")}`,
      limitCount: i % 3 === 0 ? null : (i + 1) * 2,
      expiration: i % 3 === 0 ? null : addHours(new Date(), (i + 1) * 12),
      usedCount: i,
    })),
  },
  parameters: {
    docs: {
      description: {
        story:
          "State with 8 links — a mix of active, expired, unlimited, and usage-limited. Verifies dialog scroll behavior and layout integrity.",
      },
    },
  },
};

/**
 * Case with a very long URL.
 * Verifies that text wraps or truncates correctly without breaking the layout.
 */
export const ListLongUrl: Story = {
  name: "List: Long URL",
  args: {
    initialInvitations: [
      {
        id: "1",
        link: "https://very-long-hostname.example.com/pteam/join?token=averylongtokenvaluethatmightoverflowtheuiifnothandledproperly",
        limitCount: null,
        expiration: addHours(new Date(), 24),
        usedCount: 0,
      },
    ],
  },
  parameters: {
    docs: {
      description: {
        story:
          "Checks display of a URL with a very long token segment. Verifies that `text-overflow: ellipsis` works correctly and the layout does not break.",
      },
    },
  },
};
