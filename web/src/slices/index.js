import { combineReducers } from "redux";

import system from "./system";

export const sliceReducers = { system };

const rootReducer = combineReducers(sliceReducers);

export default rootReducer;
