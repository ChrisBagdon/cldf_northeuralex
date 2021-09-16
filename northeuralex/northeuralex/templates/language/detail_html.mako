<%inherit file="../${context.get('request').registry.settings.get('clld.app_template', 'app.mako')}"/>
<%namespace name="util" file="../util.mako"/>
<%! active_menu_item = "languages" %>
<%block name="title">${_('Language')} ${ctx.name}</%block>

<h2>${_('Language')} ${ctx.name}</h2>

${request.get_datatable('values', h.models.Value, language=ctx).render()}

<% def split_input(str):
	return (str).split(";")
%>

<%def name="sidebar()">
    ${util.codes()}
    <div style="clear: right;"> </div>
    <%util:well>
        ${request.map.render()}
        ${h.format_coordinates(ctx)}
        
    </%util:well>

    
    <%util:well title="Sources">
        ${util.sources_list(sorted(list(ctx.sources), key=lambda s: s.name))}
        <div style="clear: both;"></div>
    </%util:well>
    <%util:well title="Contributors">
        % if ctx.sources_role:
            <dt>${"Sources"}</dt>
	    <dd>
	        % for c in ctx.sources_role.split(";"):
	            <li>${c.capitalize()}</li>
	        % endfor
	        </ul>
	    </dd>
	% endif
	% if ctx.data_entry:
	    <dt>${"Data Entry"}</dt>
	    <dd>
	        % for c in ctx.data_entry.split(";"):
	            <li>${c}</li>
	        % endfor
	        </ul>
	    </dd>
	% endif
	% if ctx.consultants:
	    <dt>${"Consultants"}</dt>
	    <dd>
	        % for c in ctx.consultants.split(";"):
	            <li>${c}</li>
	        % endfor
	        </ul>
	    </dd>
	% endif
    </%util:well>
    
</%def>
