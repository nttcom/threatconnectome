import { Box } from "@mui/material";
import React from "react";
import { ErrorBoundary } from "react-error-boundary";
import { useSelector } from "react-redux";

import { mainMaxWidth } from "../../utils/const";

import { AppBar } from "./AppBar";
import { AppFallback } from "./AppFallback";
import { Drawer } from "./Drawer";
import { Main } from "./Main";
import { OutletWithCheckedParams } from "./OutletWithCheckedParams";

export function App() {
  const system = useSelector((state) => state.system);

  return (
    <>
      <Box flexGrow={1}>
        <AppBar />
      </Box>
      <Drawer />
      <Main open={system.drawerOpen}>
        <Box display="flex" flexDirection="row" flexGrow={1} justifyContent="center" m={1}>
          <Box display="flex" flexDirection="column" flexGrow={1} maxWidth={mainMaxWidth}>
            <ErrorBoundary FallbackComponent={AppFallback}>
              <OutletWithCheckedParams />
            </ErrorBoundary>
          </Box>
        </Box>
      </Main>
    </>
  );
}
