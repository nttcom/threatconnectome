import { combineReducers } from "redux";

import auth from "./auth";
import system from "./system";

export const sliceReducers = { auth, system };

const rootReducer = combineReducers(sliceReducers);

export default rootReducer;
