# Copy to config/tech.tcl and fill in for your technology (git-ignored).
# Routing direction and track offset for every routing layer of your metal stack:
set routing_layers {
    {<layer1> horizontal <offset>} {<layer2> vertical <offset>}
    # ... one entry per layer
}
foreach item $routing_layers {
    set_attribute [get_layers [lindex $item 0]] routing_direction [lindex $item 1]
    set_attribute [get_layers [lindex $item 0]] track_offset      [lindex $item 2]
}
set LAYER_RAIL      <lowest metal: standard-cell power rails>
set LAYER_MESH_V    <vertical power-mesh layer>
set LAYER_ROUTE_MAX <highest layer the router may use>
