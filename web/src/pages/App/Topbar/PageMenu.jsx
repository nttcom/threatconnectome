import { MenuHeader } from "./MenuHeader";
import { MenuShell } from "./MenuShell";
import { PageMenuItem } from "./PageMenuItem";
import { menuWidths } from "./topbarStyles";

export function PageMenu({
  anchorEl,
  currentPage,
  labels,
  open,
  onClose,
  onSelectPage,
  pageItems,
}) {
  const selectPage = (item) => {
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
