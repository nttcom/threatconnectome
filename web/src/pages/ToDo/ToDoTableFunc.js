import { useState, useEffect } from "react";
import { useDispatch } from "react-redux";

import { tcApi } from "../../services/tcApi";

async function fetchTicketsForPteams(dispatch, pteamIds, myTasks) {
  const ticketPromises = pteamIds.map((pteamId) =>
    dispatch(tcApi.endpoints.getPteamTickets.initiate({ pteamId, assignedToMe: myTasks })).unwrap(),
  );
  const ticketsResults = await Promise.all(ticketPromises);
  return ticketsResults.flatMap((tickets, idx) =>
    (tickets ?? []).map((ticket) => ({ ...ticket, pteam_id: pteamIds[idx] })),
  );
}

async function fetchPteams(dispatch, pteamIds) {
  const pteamPromises = pteamIds.map((pteamId) =>
    dispatch(tcApi.endpoints.getPTeam.initiate(pteamId)).unwrap(),
  );
  const results = await Promise.all(pteamPromises);
  return new Map(pteamIds.map((id, idx) => [id, results[idx]]));
}

async function fetchServices(dispatch, tickets) {
  const serviceIds = [...new Set(tickets.map((t) => t.service_id).filter(Boolean))];
  const servicePromises = serviceIds.map((id) =>
    dispatch(tcApi.endpoints.getService.initiate(id)).unwrap(),
  );
  const results = await Promise.all(servicePromises);
  return new Map(results.map((svc) => [svc.pteam_id + ":" + svc.service_id, svc]));
}

async function fetchUsers(dispatch, pteamIds) {
  const memberPromises = pteamIds.map((pteamId) =>
    dispatch(tcApi.endpoints.getPTeamMembers.initiate(pteamId)).unwrap(),
  );
  const memberResults = await Promise.all(memberPromises);
  const userMap = new Map();
  memberResults.forEach((members) => {
    Object.values(members ?? {}).forEach((user) => {
      userMap.set(user.user_id, user.email);
    });
  });
  return userMap;
}

export function useTicketsAndPteams(pteamIds, myTasks) {
  const dispatch = useDispatch();
  const [allTickets, setAllTickets] = useState([]);
  const [pteamMap, setPteamMap] = useState(new Map());
  const [serviceMap, setServiceMap] = useState(new Map());
  const [userMap, setUserMap] = useState(new Map());
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!pteamIds?.length) {
      setAllTickets([]);
      setPteamMap(new Map());
      setServiceMap(new Map());
      setLoading(false);
      return;
    }

    let cancelled = false;
    async function fetchAll() {
      setLoading(true);
      try {
        const tickets = await fetchTicketsForPteams(dispatch, pteamIds, myTasks);
        if (cancelled) return;

        const [teams, services, users] = await Promise.all([
          fetchPteams(dispatch, pteamIds),
          fetchServices(dispatch, tickets),
          fetchUsers(dispatch, pteamIds),
        ]);
        if (cancelled) return;

        setAllTickets(tickets);
        setPteamMap(teams);
        setServiceMap(services);
        setUserMap(users);
      } catch (error) {
        console.error("fetchAll error", error);
        setAllTickets([]);
        setPteamMap(new Map());
        setServiceMap(new Map());
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    fetchAll();
    return () => {
      cancelled = true;
    };
  }, [pteamIds, myTasks, dispatch]);

  return { allTickets, pteamMap, serviceMap, userMap, loading };
}

const priorityOrder = {
  immediate: 0,
  "out-of-cycle": 1,
  scheduled: 2,
  defer: 3,
};

function descendingComparator(rowA, rowB, orderBy) {
  const rowAValue = orderBy === "ssvc" ? (priorityOrder[rowA[orderBy]] ?? Infinity) : rowA[orderBy];
  const rowBValue = orderBy === "ssvc" ? (priorityOrder[rowB[orderBy]] ?? Infinity) : rowB[orderBy];

  if (rowBValue < rowAValue) return -1;
  if (rowBValue > rowAValue) return 1;
  return 0;
}

export function getComparator(order, orderBy) {
  return order === "desc"
    ? (rowA, rowB) => descendingComparator(rowA, rowB, orderBy)
    : (rowA, rowB) => -descendingComparator(rowA, rowB, orderBy);
}
