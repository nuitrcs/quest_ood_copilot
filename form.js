'use strict'

function toggle_visibility_of_form_group(form_id, show) {
  let form_element = $(form_id);
  let parent = form_element.parent();
  if(show) {
    parent.show();
  } else {
    form_element.val('');
    parent.hide();
  }
}

function convert_timelimit(TIMELIMIT) {
  const time_split = TIMELIMIT.split(/[-:]/).map(Number);
  var time_in_hours = 0;
  if (time_split.length === 3) {
    time_in_hours = time_split[0] + time_split[1]/60 + time_split[2]/3600;
  } else if (time_split.length === 4) {
    time_in_hours = time_split[0] * 24 + time_split[1] + time_split[2]/60 + time_split[3]/3600;
  }
  return time_in_hours;
}

function replace_options($select, new_options) {
  const old_selection = $select.val();
  $select.empty();
  new_options.map(option => $select.append($("<option></option>").attr("value", option).text(option)));
  if (new_options.includes(old_selection)) {
    $select.val(old_selection);
  }
}

function get_associations() {
  const raw_data = $('#batch_connect_session_context_raw_data').val();
  const raw_groups_data = $('#batch_connect_session_context_raw_group_data').val().split(",").filter(x => x);
  const general_access_allocations = raw_groups_data.filter(x => x.startsWith("p") || x.startsWith("e"));
  const assocs = [];
  for (const assoc of raw_data.split(" ").filter(x => x)) {
    const [PARTITION, GROUPS, TIMELIMIT, GRES, MEMORY, CPUS, FEATURE] = assoc.split("|");
    const groups = raw_groups_data.filter(value => GROUPS.includes(value));
    if (PARTITION.includes("a9009") && raw_groups_data.includes("a9009")) {
      assocs.push({ partition: PARTITION,
                    account: "a9009",
                    maxtime: convert_timelimit(TIMELIMIT),
                    max_mem: MEMORY,
                    max_cpus: CPUS });
    } else if (GROUPS.includes("all") && (general_access_allocations.length !== 0) && (PARTITION !== 'a9009') && (PARTITION !== 'buyin-dev')) {
      for (let gen_access of general_access_allocations) {
        assocs.push({ partition: PARTITION.replace('*', ''),
                      account: gen_access,
                      maxtime: convert_timelimit(TIMELIMIT),
                      max_mem: MEMORY,
                      max_cpus: CPUS });
      }
    } else if (groups.length !== 0) {
      for (const group of groups) {
        assocs.push({ partition: PARTITION,
                      account: group,
                      maxtime: convert_timelimit(TIMELIMIT),
                      max_mem: MEMORY,
                      max_cpus: CPUS });
      }
    }
  }
  return assocs;
}

function set_available_accounts() {
  let assocs = get_associations();
  const selected_partition = $("#batch_connect_session_context_slurm_partition").val();
  assocs = assocs.filter(({ partition }) => partition === selected_partition);
  const accounts = [...new Set(assocs.map(({ account }) => account))];
  replace_options($("#batch_connect_session_context_slurm_account"), accounts);
  return assocs;
}

function set_min_max(assocs) {
  const max_walltime = [...new Set(assocs.map(({ maxtime }) => maxtime))][0];
  const max_mem = Number([...new Set(assocs.map(({ max_mem }) => max_mem))][0].replace('+', ''));

  $("#batch_connect_session_context_bc_num_hours").attr({
    "max": max_walltime === 0 ? "" : max_walltime,
    "min": 1,
  });

  $("#batch_connect_session_context_bc_num_memory").attr({
    "max": max_mem > 264000 ? 2000 : 968,
    "min": 1,
  });
}

function update_available_options() {
  return set_available_accounts();
}

function set_available_partitions() {
  const assocs = get_associations();
  const partitions = [...new Set(assocs.map(({ partition }) => partition))];
  replace_options($("#batch_connect_session_context_slurm_partition"), partitions);
}

function set_slurm_partition_change_handler() {
  $("#batch_connect_session_context_slurm_partition").change(() => {
    const assocs = update_available_options();
    set_min_max(assocs);
  });
}

function set_slurm_account_change_handler() {
  $("#batch_connect_session_context_slurm_account").change(() => {
    update_available_options();
  });
}

function collapse_help() {
  var help_message = $( '.form-text.text-muted' );
  $.each(help_message, function(index) {
    var form_label = $( '.form-group label' )[index];
    var help_text = $( this ).html();
    var new_help = $( `<div class="card border-dark mb-2" aria-expanded="false" role="button" data-target=#help_message_${index} aria-controls=help_message_${index} data-toggle="collapse"><div class="card-header"><button type="button" class="btn btn-outline-secondary py-0 px-1"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-arrow-down" viewBox="0 0 16 16"><path fill-rule="evenodd" d="M8 1a.5.5 0 0 1 .5.5v11.793l3.146-3.147a.5.5 0 0 1 .708.708l-4 4a.5.5 0 0 1-.708 0l-4-4a.5.5 0 0 1 .708-.708L7.5 13.293V1.5A.5.5 0 0 1 8 1z"/></button> ${form_label.textContent}</div><div class="collapse" id=help_message_${index}><div class="card-body text-dark" aria-expanded="false"><p class="card-text"><small class="form-text text-muted">${help_text}</small></p></div></div></div>` );
    new_help.insertBefore(form_label);
    form_label.textContent = '';
    form_label.hidden = 'true';
    $( this ).remove();
  });
}

$(document).ready(function() {
  set_available_partitions();
  const assocs = update_available_options();
  set_min_max(assocs);
  set_slurm_partition_change_handler();
  set_slurm_account_change_handler();
  collapse_help();
  $(function() {
    $('[data-toggle="tooltip"]').tooltip({'boundary': $("body")});
  });
});

$(document.links).filter(function() {
  return this.hostname != window.location.hostname;
}).attr('target', '_blank');
