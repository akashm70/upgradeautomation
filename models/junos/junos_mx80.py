import sys
from dataclasses import dataclass, field, asdict
import re
from typing import List, Dict, Any, Union, Optional

@dataclass
class ShowArpNoResolveEntry:
    """Represents a single ARP table entry"""
    mac_address: str
    ip_address: str
    interface: str
    flags: str

@dataclass
class ShowArpNoResolve:
    """Represents the complete ARP table output"""
    entries: List[ShowArpNoResolveEntry] = field(default_factory=list)
    total_entries: int = 0
    
    def to_dict(self):
        """Convert to dictionary format"""
        return {
            "total_entries": self.total_entries,
            "entries": [
                {
                    "mac_address": entry.mac_address,
                    "ip_address": entry.ip_address,
                    "interface": entry.interface,
                    "flags": entry.flags
                }
                for entry in self.entries
            ]
        }

@dataclass
class ShowVrrpSummaryAddress:
    """Represents a VRRP address (lcl or vip)"""
    type: str  # 'lcl' or 'vip'
    address: str

@dataclass
class ShowVrrpSummaryEntry:
    """Represents a single VRRP group entry"""
    interface: str
    state: str
    group: int
    vr_state: str
    vr_mode: str
    addresses: List[ShowVrrpSummaryAddress] = field(default_factory=list)

@dataclass
class ShowVrrpSummary:
    """Represents the complete VRRP summary output"""
    entries: List[ShowVrrpSummaryEntry] = field(default_factory=list)
    
    def to_dict(self):
        """Convert to dictionary format"""
        return {
            "entries": [
                {
                    "interface": entry.interface,
                    "state": entry.state,
                    "group": entry.group,
                    "vr_state": entry.vr_state,
                    "vr_mode": entry.vr_mode,
                    "addresses": [
                        {
                            "type": addr.type,
                            "address": addr.address
                        }
                        for addr in entry.addresses
                    ]
                }
                for entry in self.entries
            ]
        }

@dataclass
class ShowLldpNeighborsEntry:
    """Represents a single LLDP neighbor entry"""
    local_interface: str
    parent_interface: str
    chassis_id: str
    port_info: str
    system_name: str

@dataclass
class ShowLldpNeighbors:
    """Represents the complete LLDP neighbors output"""
    entries: List[ShowLldpNeighborsEntry] = field(default_factory=list)
    
    def to_dict(self):
        """Convert to dictionary format"""
        return {
            "entries": [
                {
                    "local_interface": entry.local_interface,
                    "parent_interface": entry.parent_interface,
                    "chassis_id": entry.chassis_id,
                    "port_info": entry.port_info,
                    "system_name": entry.system_name
                }
                for entry in self.entries
            ]
        }

@dataclass
class ShowBfdSessionEntry:
    """Represents a single BFD session entry"""
    address: str
    state: str
    interface: str
    detect_time: str
    transmit_interval: str
    multiplier: str

@dataclass
class ShowBfdSession:
    """Represents the complete BFD session output"""
    entries: List[ShowBfdSessionEntry] = field(default_factory=list)
    total_sessions: int = 0
    total_clients: int = 0
    cumulative_transmit_rate: str = ""
    cumulative_receive_rate: str = ""
    
    def to_dict(self):
        """Convert to dictionary format"""
        return {
            "total_sessions": self.total_sessions,
            "total_clients": self.total_clients,
            "cumulative_transmit_rate": self.cumulative_transmit_rate,
            "cumulative_receive_rate": self.cumulative_receive_rate,
            "entries": [
                {
                    "address": entry.address,
                    "state": entry.state,
                    "interface": entry.interface,
                    "detect_time": entry.detect_time,
                    "transmit_interval": entry.transmit_interval,
                    "multiplier": entry.multiplier
                }
                for entry in self.entries
            ]
        }

@dataclass
class ShowRouteTableInet3NextHop:
    """Represents a single next-hop for a route"""
    to: str
    via: str
    mpls_label: str = ""

@dataclass
class ShowRouteTableInet3Entry:
    """Represents a single route entry with multiple next-hops"""
    destination: str
    protocol: str
    preference: str
    metric: str
    age: str
    next_hops: List[ShowRouteTableInet3NextHop] = field(default_factory=list)

@dataclass
class ShowRouteTableInet3:
    """Represents the complete inet.3 routing table output"""
    total_destinations: int = 0
    total_routes: int = 0
    active_routes: int = 0
    holddown_routes: int = 0
    hidden_routes: int = 0
    entries: List[ShowRouteTableInet3Entry] = field(default_factory=list)
    
    def to_dict(self):
        """Convert to dictionary format"""
        return {
            "total_destinations": self.total_destinations,
            "total_routes": self.total_routes,
            "active_routes": self.active_routes,
            "holddown_routes": self.holddown_routes,
            "hidden_routes": self.hidden_routes,
            "entries": [
                {
                    "destination": entry.destination,
                    "protocol": entry.protocol,
                    "preference": entry.preference,
                    "metric": entry.metric,
                    "age": entry.age,
                    "next_hops": [
                        {
                            "to": nh.to,
                            "via": nh.via,
                            "mpls_label": nh.mpls_label
                        }
                        for nh in entry.next_hops
                    ]
                }
                for entry in self.entries
            ]
        }

@dataclass
class ShowRouteTableMpls0NextHop:
    """Represents a single next-hop entry in mpls.0 routing table"""
    to: Optional[str] = None
    via: Optional[str] = None
    action: Optional[str] = None  # Pop, Swap, Push, Receive, etc.
    mpls_label: Optional[str] = None
    lsp_name: Optional[str] = None

@dataclass
class ShowRouteTableMpls0Entry:
    """Represents a single route entry in mpls.0 routing table"""
    label: str = ""
    protocol: str = ""
    preference: str = ""
    metric: str = ""
    age: str = ""
    next_hops: List[ShowRouteTableMpls0NextHop] = field(default_factory=list)

@dataclass
class ShowRouteTableMpls0:
    """Represents the complete mpls.0 routing table output"""
    total_destinations: int = 0
    total_routes: int = 0
    active_routes: int = 0
    holddown_routes: int = 0
    hidden_routes: int = 0
    entries: List[ShowRouteTableMpls0Entry] = field(default_factory=list)
    
    def to_dict(self):
        """Convert to dictionary format"""
        return {
            "total_destinations": self.total_destinations,
            "total_routes": self.total_routes,
            "active_routes": self.active_routes,
            "holddown_routes": self.holddown_routes,
            "hidden_routes": self.hidden_routes,
            "entries": [
                {
                    "label": entry.label,
                    "protocol": entry.protocol,
                    "preference": entry.preference,
                    "metric": entry.metric,
                    "age": entry.age,
                    "next_hops": [
                        {
                            "to": nh.to,
                            "via": nh.via,
                            "action": nh.action,
                            "mpls_label": nh.mpls_label,
                            "lsp_name": nh.lsp_name
                        }
                        for nh in entry.next_hops
                    ]
                }
                for entry in self.entries
            ]
        }

@dataclass
class ShowRsvpNeighborEntry:
    address: str
    idle: int
    up_dn: str
    last_change: str
    hello_interval: int
    hello_tx_rx: str
    msg_rcvd: int

@dataclass
class ShowRsvpNeighbor:
    total_neighbors: int = 0
    entries: List[ShowRsvpNeighborEntry] = field(default_factory=list)

@dataclass
class ShowMplsInterfaceEntry:
    """Represents a single MPLS interface entry"""
    interface: str
    state: str
    administrative_groups: str

@dataclass
class ShowMplsInterface:
    """Represents the complete MPLS interface output"""
    entries: List[ShowMplsInterfaceEntry] = field(default_factory=list)
    
    def to_dict(self):
        """Convert to dictionary format"""
        return {
            "entries": [
                {
                    "interface": entry.interface,
                    "state": entry.state,
                    "administrative_groups": entry.administrative_groups
                }
                for entry in self.entries
            ]
        }

@dataclass
class ShowIsisAdjacencyTransition:
    """Represents a single transition log entry"""
    when: str
    state: str
    event: str
    down_reason: str = ""

@dataclass
class ShowIsisAdjacencyEntry:
    """Represents a single ISIS adjacency"""
    system_name: str
    interface: str
    level: str
    state: str
    expires_in: str
    priority: str
    up_down_transitions: int
    last_transition: str
    circuit_type: str
    speaks: str
    topologies: str
    restart_capable: str
    adjacency_advertisement: str
    ip_addresses: List[str] = field(default_factory=list)
    adj_sids: List[Dict[str, str]] = field(default_factory=list)
    transition_log: List[ShowIsisAdjacencyTransition] = field(default_factory=list)

@dataclass
class ShowIsisAdjacencyExtensive:
    """Represents the complete ISIS adjacency extensive output"""
    entries: List[ShowIsisAdjacencyEntry] = field(default_factory=list)
    
    def to_dict(self):
        """Convert to dictionary format"""
        return {
            "entries": [
                {
                    "system_name": entry.system_name,
                    "interface": entry.interface,
                    "level": entry.level,
                    "state": entry.state,
                    "expires_in": entry.expires_in,
                    "up_down_transitions": entry.up_down_transitions,
                    "last_transition": entry.last_transition,
                    "ip_addresses": entry.ip_addresses,
                    "adj_sids": entry.adj_sids,
                    "transition_log": [
                        {
                            "when": t.when,
                            "state": t.state,
                            "event": t.event,
                            "down_reason": t.down_reason
                        }
                        for t in entry.transition_log
                    ]
                }
                for entry in self.entries
            ]
        }

@dataclass
class ShowRouteSummaryHighwater:
    """Represents highwater mark statistics"""
    rib_unique_destination_routes: str = ""
    rib_routes: str = ""
    fib_routes: str = ""
    vrf_type_routing_instances: str = ""

@dataclass
class ShowRouteSummaryProtocol:
    """Represents protocol statistics for a routing table"""
    protocol: str
    routes: int
    active: int

@dataclass
class ShowRouteSummaryTable:
    """Represents a routing table summary"""
    table_name: str
    destinations: int
    routes: int
    active: int
    holddown: int
    hidden: int
    protocols: List[ShowRouteSummaryProtocol] = field(default_factory=list)

@dataclass
class ShowRouteSummary:
    """Represents the complete route summary output"""
    autonomous_system: str = ""
    router_id: str = ""
    highwater: Optional[ShowRouteSummaryHighwater] = None
    tables: List[ShowRouteSummaryTable] = field(default_factory=list)
    
    def to_dict(self):
        """Convert to dictionary format"""
        result = {
            "autonomous_system": self.autonomous_system,
            "router_id": self.router_id,
            "tables": [
                {
                    "table_name": table.table_name,
                    "destinations": table.destinations,
                    "routes": table.routes,
                    "active": table.active,
                    "holddown": table.holddown,
                    "hidden": table.hidden,
                    "protocols": [
                        {
                            "protocol": proto.protocol,
                            "routes": proto.routes,
                            "active": proto.active
                        }
                        for proto in table.protocols
                    ]
                }
                for table in self.tables
            ]
        }
        
        if self.highwater:
            result["highwater"] = {
                "rib_unique_destination_routes": self.highwater.rib_unique_destination_routes,
                "rib_routes": self.highwater.rib_routes,
                "fib_routes": self.highwater.fib_routes,
                "vrf_type_routing_instances": self.highwater.vrf_type_routing_instances
            }
        
        return result


@dataclass
class RsvpSessionIngressEntry:
    to: str
    from_: str
    state: str
    rt: int
    style: str
    label_in: str
    label_out: str
    lsp_name: str

@dataclass
class RsvpSessionEgressEntry:
    to: str
    from_: str
    state: str
    rt: int
    style: str
    label_in: str
    label_out: str
    lsp_name: str

@dataclass
class RsvpSessionTransitEntry:
    to: str
    from_: str
    state: str
    rt: int
    style: str
    label_in: str
    label_out: str
    lsp_name: str

@dataclass
class ShowRsvpSession:
    ingress_sessions: int = 0
    ingress_up: int = 0
    ingress_down: int = 0
    ingress_entries: List[RsvpSessionIngressEntry] = field(default_factory=list)
    
    egress_sessions: int = 0
    egress_up: int = 0
    egress_down: int = 0
    egress_entries: List[RsvpSessionEgressEntry] = field(default_factory=list)
    
    transit_sessions: int = 0
    transit_up: int = 0
    transit_down: int = 0
    transit_entries: List[RsvpSessionTransitEntry] = field(default_factory=list)

@dataclass
class MplsLspIngressEntry:
    to: str
    from_: str
    state: str
    rt: int
    p: str
    active_path: str
    lsp_name: str

@dataclass
class MplsLspEgressEntry:
    to: str
    from_: str
    state: str
    rt: int
    style: str
    label_in: str
    label_out: str
    lsp_name: str

@dataclass
class MplsLspTransitEntry:
    to: str
    from_: str
    state: str
    rt: int
    style: str
    label_in: str
    label_out: str
    lsp_name: str

@dataclass
class ShowMplsLsp:
    ingress_sessions: int = 0
    ingress_up: int = 0
    ingress_down: int = 0
    ingress_entries: List[MplsLspIngressEntry] = field(default_factory=list)
    egress_sessions: int = 0
    egress_up: int = 0
    egress_down: int = 0
    egress_entries: List[MplsLspEgressEntry] = field(default_factory=list)
    transit_sessions: int = 0
    transit_up: int = 0
    transit_down: int = 0
    transit_entries: List[MplsLspTransitEntry] = field(default_factory=list)

@dataclass
class RsvpSessionEntry:
    to_address: str
    from_address: str
    state: str
    rt: int
    style: str
    label_in: str
    label_out: str
    lsp_name: str

@dataclass
class RsvpSection:
    section_type: str
    total_sessions: int
    sessions_up: int
    sessions_down: int
    entries: List[RsvpSessionEntry] = field(default_factory=list)

@dataclass
class ShowRsvpData:
    ingress: RsvpSection = None
    egress: RsvpSection = None
    transit: RsvpSection = None

@dataclass
class MplsLspEntry:
    to_address: str
    from_address: str
    state: str
    rt: int
    style: str
    label_in: str
    label_out: str
    lsp_name: str

@dataclass
class MplsLspSection:
    section_type: str
    total_sessions: int
    sessions_displayed: int
    sessions_up: int
    sessions_down: int
    entries: List[MplsLspEntry] = field(default_factory=list)

@dataclass
class ShowMplsLspData:
    ingress: MplsLspSection = None
    egress: MplsLspSection = None
    transit: MplsLspSection = None

@dataclass
class RouteEntry:
    destination: str
    protocol: str
    preference: int
    metric: int
    age: str
    next_hop: str
    interface: str
    flags: str = ""

@dataclass
class RouteTableData:
    table_name: str
    total_destinations: int
    total_routes: int
    active_routes: int
    holddown_routes: int
    hidden_routes: int
    entries: List[RouteEntry] = field(default_factory=list)

@dataclass
class RsvpNeighborEntry:
    address: str
    idle: int
    up_down: str
    last_change: str
    hello_int: int
    hello_tx_rx: str
    msg_rcvd: int

@dataclass
class ShowRsvpNeighborData:
    total_neighbors: int = 0  
    neighbors: List[RsvpNeighborEntry] = field(default_factory=list)

# Data Models for P2MP LSP
@dataclass
class P2MPIngressBranch:
    to: str
    from_: str
    state: str
    rt: int
    p: str
    active_path: str
    lsp_name: str

@dataclass
class P2MPEgressBranch:
    to: str
    from_: str
    state: str
    rt: int
    style: str
    label_in: str
    label_out: str
    lsp_name: str

@dataclass
class P2MPTransitBranch:
    to: str
    from_: str
    state: str
    rt: int
    style: str
    label_in: str
    label_out: str
    lsp_name: str

@dataclass
class P2MPSession:
    p2mp_name: str
    branch_count: int
    branches: List[Union[P2MPIngressBranch, P2MPEgressBranch, P2MPTransitBranch]] = field(default_factory=list)

@dataclass
class P2MPLSPSection:
    total_sessions: int = 0
    sessions_displayed: int = 0
    sessions_up: int = 0
    sessions_down: int = 0
    sessions: List[P2MPSession] = field(default_factory=list)

@dataclass
class ShowMplsLspP2MP:
    ingress_lsp: P2MPLSPSection = field(default_factory=P2MPLSPSection)
    egress_lsp: P2MPLSPSection = field(default_factory=P2MPLSPSection)
    transit_lsp: P2MPLSPSection = field(default_factory=P2MPLSPSection)