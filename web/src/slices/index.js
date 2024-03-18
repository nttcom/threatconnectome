import { combineReducers } from "redux";

import ateam from "./ateam";
import pteam from "./pteam";
import system from "./system";
import tags from "./tags";
import topics from "./topics";
import user from "./user";

const rootReducer = combineReducers({ ateam, pteam, system, tags, topics, user });

export default rootReducer;
