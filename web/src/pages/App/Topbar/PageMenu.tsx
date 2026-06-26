import { MenuHeader } from "./MenuHeader";
import { MenuShell } from "./MenuShell";
import { PageMenuItem } from "./PageMenuItem";
import { menuWidths } from "./topbarStyles";
import type { MenuAnchor, TopbarLabels, TopbarPageItem } from "./topbarTypes";

type PageMenuProps = {
  anchorEl: MenuAnchor;
  currentPage: TopbarPageItem;
  labels: TopbarLabels;
  open: boolean;
  onClose: () => void;
  onSelectPage: (item: TopbarPageItem) => void;
  pageItems: TopbarPageItem[];
};

export function PageMenu({
  anchorEl,
  currentPage,
  labels,
  open,
  onClose,
  onSelectPage,
  pageItems,
}: PageMenuProps) {
  const selectPage = (item: TopbarPageItem) => {
    onSelectPage(item);
    onClose();
  };

  return (
    <MenuShell
      anchorEl={anchorEl}
      ariaLabel={labels.pageSwitch}
      open={open}
      onClose={onClose}
      width={menuWidths.page}
    >
      <MenuHeader title={labels.pageSwitch} />
      {pageItems.map((item) => (
        <PageMenuItem
          key={item.id}
          current={item.id === currentPage.id}
          item={item}
          labels={labels}
          onSelect={selectPage}
        />
      ))}
    </MenuShell>
  );
}
