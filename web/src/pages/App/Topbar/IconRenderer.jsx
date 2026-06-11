export function IconRenderer({ icon: Icon, size = 18 }) {
  return <Icon aria-hidden="true" sx={{ fontSize: size }} />;
}
