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
        $(document).on('click',".attr_name",function () {
          event.preventDefault();
          $(context + " #figure").load("http://127.0.0.1:8000/plots/histogram/"+$(this).attr("value")+"?id="+id);
        });
      });
}

function register_cell_table(context,id){
    $(document).ready(function () {
        $(context + " #row-select,#column-select" ).change(function() {
          $(context + " #table").load("http://127.0.0.1:8000/table/"+$( "#row-select option:selected" ).attr("value")+"/"+$( "#column-select option:selected" ).attr("value")+"?id="+id);
          $(context + " #btn-create-cell").removeAttr('disabled');
        });
      });
}

function register_dfg(context,id){
    $(document).ready(function () {
        $(document).on("click", "#btn-dfg", function () {
          event.preventDefault();
          $(context + " #btn-dfg-loading").show()
          $(context + " #btn-dfg").hide()
          $("#dfg").load(
            "http://127.0.0.1:8000/plots/dfg" + "?id="+id+"&act_freq="+$("#range-act-freq").val()+"&edge_freq="+$("#range-edge-freq").val(), function() {
              $(context + " #btn-dfg-loading").hide()
              $(context + " #btn-dfg").show()
            });
        });
      });
}