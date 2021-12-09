function register_oc_table(context){
    $(document).ready(function () {
        $(context + " .event-level").change(function() {
        if(this.checked) {
            //$("#"+$(this).attr("name")).show("slow")
            $(context + " #"+$(this).attr("name")).addClass("d-flex").removeClass("d-none");
        }
        else{
        //$("#"+$(this).attr("name")).hide("slow")
        $(context + " #"+$(this).attr("name")).removeClass("d-flex").addClass("d-none");
        }
        });
    });
}

function register_histogram(context,id){
    $(document).ready(function () {
        $(context + " .attr_name").on('click',function () {
          event.preventDefault();
          $(context + " #figure").load("/plots/histogram/"+$(this).attr("value")+"?id="+id);
        });
      });
}

function register_cell_table(context,id){
    $(document).ready(function () {
        $(context + " #row-select,#column-select" ).change(function() {
          $(context + " #table").html('<div class="spinner-border" role="status"></div>');
          $(context + " #table").load("/table/"+$( "#row-select option:selected" ).attr("value")+"/"+$( "#column-select option:selected" ).attr("value")+"?id="+id);
          $(context + " #btn-create-cell").removeAttr('disabled');
        });
      });
}

function register_vis_buttons(context,id){
    $(document).ready(function () {
        $(document).on("click", "#btn-dfg-freq", function () {
          event.preventDefault();
          loading_show(context,"#btn-dfg-freq")
          $("#dfg").load(
            "/plots/dfg" + "?id="+id
            +"&act_freq="+$("#div-dfg #range-act-freq").val()
            +"&edge_freq="+$("#div-dfg #range-edge-freq").val()
            +"&measure=frequency", function() {
              loading_hide(context,"#btn-dfg-freq")
            });
        });
        $(document).on("click", "#btn-dfg-perf", function () {
          event.preventDefault();
          loading_show(context,"#btn-dfg-perf")
          $("#dfg").load(
            "/plots/dfg" 
            + "?id="+id
            +"&act_freq="+$("#div-dfg #range-act-freq").val()
            +"&edge_freq="+$("#div-dfg #range-edge-freq").val()
            +"&measure=performance", function() {
              loading_hide(context,"#btn-dfg-perf")
            });
        });
        $(document).on("click", "#btn-petri", function () {
          event.preventDefault();
          loading_show(context,"#btn-petri")
          $("#petri").load(
            "/plots/petri" 
            + "?id="+id
            +"&act_freq="+$("#div-petri #range-act-freq").val()
            +"&edge_freq="+$("#div-petri #range-edge-freq").val(), function() {
              loading_hide(context,"#btn-petri")
            });
        });
    });
}

function onclick_hide_show(context,element,normal,loading){
  $(document).ready(function () {
    $(context + " " +element).on("click", function () {
      $(context + " " + normal).hide();
      $(context + " " + loading).show();
  });
  });
}

function loading_show(context,button){
  $(context + " " + button +"-loading").show()
  $(context + " " + button).hide()
}

function loading_hide(context,button){
  $(context + " " + button +"-loading").hide()
  $(context + " " + button).show()
}

function set_navbar_active(element){
  $(document).ready(function () {
    $(element).addClass("active")
  });
}