<html>
  <head>
    <style type="text/css">
      /* classes used to simulate tables from divs allowing beter page breaking decisions */
      .act_as_table {
        display: table;
        border: 1px solid lightGrey;
      }
      .act_as_row  {
        display: table-row;
        page-break-after: auto;
      }
      .act_as_row:nth-child(even) {
        background-color: #F0F0F0;
      }
      .act_as_cell {
        display: table-cell;
        page-break-inside: avoid;
      }
      .act_as_thead {
        display: table-header-group;
        page-break-before: auto;
      }
      .act_as_tbody {
        display: table-row-group;
      }

      .list_table, .data_table {
        width: 100%;
        table-layout: fixed;
      }

      .act_as_row.labels {
        background-color: #F0F0F0;
        font-weight: bold;
      }

      .list_table, .list_table .act_as_row {
        border-left: 0px;
        border-right: 0px;
        text-align: left;
        padding-right: 3px;
        padding-left: 3px;
        padding-top: 2px;
        padding-bottom: 2px;
        border-collapse: collapse;
      }

      .list_table .act_as_row.labels, .list_table .act_as_row.lines {
        border-color: lightGrey;
        border-bottom: 1px solid lightGrey;
      }

      .act_as_cell.amount {
        word-wrap: normal;
        text-align: right;
      }

      .list_table .act_as_cell {
        padding-left: 5px;
        /*  border-right: 1px solid lightGrey;  uncomment to active column lines */
      }
      .list_table .act_as_cell.first_column {
        padding-left: 20px;
        /*  font-weight: bold; */
        /*  border-left: 1px solid lightGrey; uncomment to active column lines */
      }

      .list_table .act_as_cell.company_column {
        padding-left: 0px;
        font-weight: bold;
        /*  border-left: 1px solid lightGrey; uncomment to active column lines */
      }

      .list_table .act_as_cell.department_column {
        padding-left: 10px;
        font-weight: bold;font-style:italic;
        /*  border-left: 1px solid lightGrey; uncomment to active column lines */
      }

      .overflow_ellipsis {
        text-overflow: ellipsis;
        overflow: hidden;
        white-space: nowrap;
      }
    </style>
  </head>
  <body>
    <%
      lines = {id: line for (id, has_schedule), line in data['res'].items() if 'pct' in line}
      departments = {id: line for (id, has_schedule), line in data['res_department'].items() if has_schedule}
      companies = [line for (id, has_schedule), line in data['res_company'].items() if has_schedule]
      lines_nc = {id: line for (id, has_schedule), line in data['res'].items() if 'pct' not in line}
      departments_nc = {id: line for (id, has_schedule), line in data['res_department'].items() if not has_schedule}
      companies_nc = [line for (id, has_schedule), line in data['res_company'].items() if not has_schedule]

      column_names = data['column_names']
      nb_cols=len(column_names)+2
      w1=100.0/(nb_cols+int(data['with_fte']))
      w2=100.0/nb_cols
      sort = data['sort_criteria']
      def pct(v):
          if not v:
              return ""
          else:
              return "%.f %%" % (v*100,)
      def hrs(v):
          if not v:
              return ""
          else:
              return "%.f h" % (v,)
    %>
    <h1>${_("Utilization report from %s to %s") % (formatLang(data['period_start'], date=True), formatLang(data['period_end'], date=True))}</h1>
    <div class="act_as_table list_table">
      <div class="act_as_thead"><div class="act_as_row labels">
        <div class="act_as_cell first_column">${_("Users")}</div>
        %for column_name in column_names:
          <div class="act_as_cell amount" style="width: ${w1}%">${column_name}</div>
        %endfor
        %if data['with_fte']:
          <div class="act_as_cell amount" style="width: ${w1}%">${_("FTE")}</div>
        %endif
      </div></div>
      <div class="act_as_tbody">
        <!-- total line, then all lines sorted by sort criteria and group by company and department -->
        %for u in [data['res_total']]:
            <div class="act_as_row lines">
              <div class="act_as_cell first_column overflow_ellipsis">${u['name']}</div>
              %for column_name in column_names:
                <div class="act_as_cell amount" style="width: ${w1}%">${hrs(u['hours'][column_name])}<br/>${pct(u['pct'][column_name])}</div>
              %endfor
              %if data['with_fte']:
                <div class="act_as_cell amount" style="width: ${w1}%">${u['fte']}</div>
              %endif
            </div>
        %endfor
        %for company in companies:
          %if company['name']:
            <div class="act_as_row lines">
              <div class="act_as_cell company_column overflow_ellipsis">${company['name']}</div>
              %for column_name in column_names:
                <div class="act_as_cell amount" style="width: ${w1}%">${hrs(company['hours'][column_name])}<br/>${pct(company['pct'][column_name])}</div>
              %endfor
              %if data['with_fte']:
                <div class="act_as_cell amount" style="width: ${w1}%">${company['fte']}</div>
              %endif
            </div>
          %endif
          %for department_id, department in departments.items(): 
            %if department['name'] and department_id in company['departments']:
              <div class="act_as_row lines">
                <div class="act_as_cell department_column overflow_ellipsis">${department['name']}</div>
                %for column_name in column_names:
                  <div class="act_as_cell amount" style="width: ${w1}%">${hrs(department['hours'][column_name])}<br/>${pct(department['pct'][column_name])}</div>
                %endfor
                %if data['with_fte']:
                  <div class="act_as_cell amount" style="width: ${w1}%">${company['fte']}</div>
                %endif
              </div>
            %endif
            %for user_id, u in sorted(lines.items(), key=lambda u: -u[1]['pct'][sort]):
              %if user_id in department['users'] and user_id in company['users']:
                <div class="act_as_row lines">
                  <div class="act_as_cell first_column overflow_ellipsis">${u['name']}</div>
                  %for column_name in column_names:
                    <div class="act_as_cell amount" style="width: ${w1}%">${hrs(u['hours'][column_name])}<br/>${pct(u['pct'][column_name])}</div>
                  %endfor
                  %if data['with_fte']:
                    <div class="act_as_cell amount" style="width: ${w1}%">${u['fte']}</div>
                  %endif
                </div>
              %endif
            %endfor
          %endfor
        %endfor
      </div>
    </div>
    %if data['fte_na']:
      <p>${_("Remark: if no full-time calendar is defined for a company, FTE values related to its users are mentionned N/A")}.</p>
    %endif
    %if data['users_without_contract']:
      <p>${_("The following users have entered timesheets but are not displayed in the table above because they have either no contract defined or no working schedule defined on their contract")}:</p>
      <div class="act_as_table list_table">
        <div class="act_as_thead"><div class="act_as_row labels">
          <div class="act_as_cell first_column">${_("Users")}</div>
          %for column_name in column_names:
            <div class="act_as_cell amount" style="width: ${w2}%">${column_name}</div>
          %endfor
        </div></div>
        <div class="act_as_tbody">
          %for u in [data['res_nc_total']]:
            <div class="act_as_row lines">
              <div class="act_as_cell first_column overflow_ellipsis">${u['name']}</div>
              %for column_name in column_names:
                <div class="act_as_cell amount" style="width: ${w2}%">${hrs(u['hours'][column_name])}</div>
              %endfor
            </div>
          %endfor
          %for company in companies_nc:
            %if company['name']:
              <div class="act_as_row lines">
                <div class="act_as_cell company_column overflow_ellipsis">${company['name']}</div>
                %for column_name in column_names:
                  <div class="act_as_cell amount" style="width: ${w2}%">${hrs(company['hours'][column_name])}</div>
                %endfor
              </div>
            %endif
            %for department_id, department in departments_nc.items(): 
              %if department['name'] and department_id in company['departments']:
                <div class="act_as_row lines">
                  <div class="act_as_cell department_column overflow_ellipsis">${department['name']}</div>
                  %for column_name in column_names:
                    <div class="act_as_cell amount" style="width: ${w2}%">${hrs(company['hours'][column_name])}</div>
                  %endfor
                </div>
              %endif
              %for user_id, u in sorted(lines_nc.items(), key=lambda u: -u[1]['hours'][sort]):
                %if user_id in department['users'] and user_id in company['users']:
                  <div class="act_as_row lines">
                    <div class="act_as_cell first_column overflow_ellipsis">${u['name']}</div>
                    %for column_name in column_names:
                      <div class="act_as_cell amount" style="width: ${w2}%">${hrs(u['hours'][column_name])}</div>
                    %endfor
                  </div>
                %endif
              %endfor
            %endfor
          %endfor
        </div>
      </div>
    %endif
  </body>
</html>
