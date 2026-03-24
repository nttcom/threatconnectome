import { http, HttpResponse } from "msw";
import { addHours } from "date-fns";
import type { Meta, StoryObj } from "@storybook/react-vite";

import { InvitationManageDialog } from "./InvitationManageDialog";

const pteamId = "team-123";

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
    pteamId: {
      description: "Team ID to display",
      control: "text",
    },
  },
  args: {
    pteamId: pteamId,
  },
} satisfies Meta<typeof InvitationManageDialog>;

export default meta;
type Story = StoryObj<typeof meta>;

/**
 * Normal state with a mix of active and expired links.
 * Shows the difference in status badge color/text and the behavior of copy/revoke buttons.
 */
export const ListWithInvitations: Story = {
  name: "List: Normal (multiple links)",
  parameters: {
    docs: {
      description: {
        story:
          "State with 2 active links. An unlimited/no-expiration link and a usage-limited/expiring link are shown side by side. The 'Revoke' button removes a link from the list.",
      },
    },
    msw: {
      handlers: [
        http.get(`*/pteams/${pteamId}/invitation`, () => {
          return HttpResponse.json([
            {
              invitation_id: "1",
              pteam_id: pteamId,
              expiration: addHours(new Date(), 1),
              limitCount: null,
              usedCount: 0,
            },
            {
              invitation_id: "2",
              pteam_id: pteamId,
              expiration: addHours(new Date(), 24),
              limitCount: 5,
              usedCount: 0,
            },
          ]);
        }),
      ],
    },
  },
};

/**
 * State with no issued links.
 * Verifies that the empty state message is displayed.
 */
export const ListEmpty: Story = {
  name: "List: Empty (0 links)",
  parameters: {
    docs: {
      description: {
        story:
          "Initial state with no invitation links. A message saying 'No active invitation links' is displayed. The 'Create New' button navigates to the creation form.",
      },
    },
    msw: {
      handlers: [
        http.get(`*/pteams/${pteamId}/invitation`, () => {
          return HttpResponse.json([]);
        }),
      ],
    },
  },
};

/**
 * For verifying scrolling behavior when a large number of links exist.
 * Checks that no layout breakage occurs.
 */
export const ListManyInvitations: Story = {
  name: "List: Many links (8 items)",
  parameters: {
    docs: {
      description: {
        story:
          "State with 8 links — a mix of active, expired, unlimited, and usage-limited. Verifies dialog scroll behavior and layout integrity.",
      },
    },
    msw: {
      handlers: [
        http.get(`*/pteams/${pteamId}/invitation`, () => {
          const responseDate = Array.from({ length: 8 }, (_, i) => ({
            invitation_id: String(i + 1),
            pteam_id: pteamId,
            expiration: i % 3 === 0 ? null : addHours(new Date(), (i + 1) * 12),
            limitCount: i % 3 === 0 ? null : (i + 1) * 2,
            usedCount: i,
          }));
          return HttpResponse.json(responseDate);
        }),
      ],
    },
  },
};

/**
 * Case with a very long URL.
 * Verifies that text wraps or truncates correctly without breaking the layout.
 */
export const ListLongUrl: Story = {
  name: "List: Long URL",
  parameters: {
    docs: {
      description: {
        story:
          "Checks display of a URL with a very long token segment. Verifies that `text-overflow: ellipsis` works correctly and the layout does not break.",
      },
    },
    msw: {
      handlers: [
        http.get(`*/pteams/${pteamId}/invitation`, () => {
          return HttpResponse.json([
            {
              invitation_id: "averylongtokenvaluethatmightoverflowtheuiifnothandledproperly",
              pteam_id: pteamId,
              expiration: addHours(new Date(), 1),
              limitCount: null,
              usedCount: 0,
            },
          ]);
        }),
      ],
    },
  },
};
