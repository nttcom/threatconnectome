import { createContext, useContext } from "react";

export interface VulnDialogContextType {
  vulnId: string;
}

const VulnDialogContext = createContext<VulnDialogContextType | undefined>(undefined);

export const useVulnDialogContext = (): VulnDialogContextType => {
  const context = useContext(VulnDialogContext);
  if (!context) {
    throw new Error("useVulnDialogContext must be used within VulnDialogProvider");
  }
  return context;
};

export default VulnDialogContext;
