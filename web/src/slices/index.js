import { combineReducers } from "redux";

import ateam from "./ateam";
import auth from "./auth";
import pteam from "./pteam";
import system from "./system";

export const sliceReducers = { ateam, auth, pteam, system };

const rootReducer = combineReducers(sliceReducers);

export default rootReducer;
