/* Javascript library for the PyScada-LaboREM web client based on jquery,

version 0.7.2

Copyright (c) 2018 Camille Lavayssière
Licensed under the GPL.

*/

$('button.write-task-form-top10-set').click(function(){
    name_form = $(this.form).attr('name');
    tabinputs = document.forms[name_form].getElementsByTagName("input");
    request_data = {}
    for (i=0;i<tabinputs.length;i++){
        j=i+1;
        value = $(tabinputs[i]).val();
        var_name = $(tabinputs[i]).attr("name");
        $.each($('.variable-config'),function(kkey,val){
            name_var = $(val).data('name');
            if (name_var==var_name){
                key = parseInt($(val).data('key'));
                //request_data.push("value" + key + ":" + value);
                request_data['value'+j] = value;
                //item_type = $(val).data('type');
            }
        });
    };
    if (request_data[0] == 'value1:' && request_data[1] == 'value2:' && request_data[2] == 'value3:' && request_data[3] == 'value4:'){
        add_notification('please provide a value',3);
        alert("data empty");
    }else{
        $.ajax({
            type: 'post',
            url: ROOT_URL+'form/validate_top10_answers/',
            data:request_data,
            success: function (data) {

            },
            error: function(data) {
                add_notification('add new write task failed',3);
                alert("Form Set NOK "+data+" - key "+key+" - value "+value+" - item_type "+item_type + " - name "+var_name)
            }
        });
    };
    reload_top10_ranking();
});

function reload_top10_ranking() {
    $.ajax({
        type: 'post',
        url: ROOT_URL+'form/rank_top10/',
        data: {},
        success: function (data) {

        },
        error: function(data) {
            add_notification('rank top10 failed',3);
        }
    });
};

$( document ).ready(function() {
    // actualize the picture of the dut selector for laborem with the list selection
    $('.list-group-item').on('click', function() {
        var $this = $(this);
        var $img = $this.data('img');
        var $mb_id = $this.data('motherboard-id');
        var $plug_id = $this.data('plug-id');

        $('.active').removeClass('active');
        $this.toggleClass('active');

        // Pass clicked link element to another function
        change_plug_img($this, $img)
        change_plug_selected_motherboard($mb_id, $plug_id)
    })
    function change_plug_img($this, $img) {
        $(".img-plug").attr("src",$img);
    }
    function change_plug_selected_motherboard(mb_id, plug_id) {
        if (mb_id == "" || plug_id == ""){
            add_notification('mb_id or plug_id empty',3);
        }else{
            $.ajax({
                type: 'post',
                url: ROOT_URL+'form/write_plug/',
                data: {mb_id:mb_id, plug_id:plug_id},
                success: function (data) {

                },
                error: function(data) {
                    add_notification('write plug selected failed',3);
                }
            });
        };
    }
    // Active the selected item in a listbox and disable it in others listboxes
    $('.dropdown-base').on('click', function() {
        var $this = $(this);
        dropdown_item = document.getElementsByClassName("dropdown-base")
        for (i=0;i<dropdown_item.length;i++){
            if ($(dropdown_item[i]).context.parentElement.parentElement.id !== $this.context.parentElement.parentElement.id) {
                if ($(dropdown_item[i]).context.id == $this.context.id) {
                    $(dropdown_item[i]).addClass('disabled');
                }
                else {
                    $(dropdown_item[i]).removeClass('disabled');
                }
            }
            else {
            $(dropdown_item[i]).removeClass('active');
            }
        }
        $this.context.parentElement.parentElement.firstElementChild.firstChild.data = $this.context.textContent;
        $this.addClass('active');
        change_base_selected_element($this.context.parentElement.parentElement.id, $this.context.id)
    })
    function change_base_selected_element(base_id, element_id) {
        if (base_id == "" || element_id == ""){
            add_notification('base_id or element_id empty',3);
        }else{
            $.ajax({
                type: 'post',
                url: ROOT_URL+'form/write_robot_base/',
                data: {base_id:base_id, element_id:element_id},
                success: function (data) {

                },
                error: function(data) {
                    add_notification('write plug selected failed',3);
                }
            });
        };
    }
    // Active the selected item in a listbox and disable it in others listboxes
    $('.dropdown-afg-function').on('click', function() {
        var $this = $(this);
        //$('.dropdown-afg-function').$('.active').removeClass('active');
        dropdown_item = document.getElementsByClassName("dropdown-afg-function")
        for (i=0;i<dropdown_item.length;i++){
            if ($(dropdown_item[i]).context.parentElement.parentElement.id == $this.context.parentElement.parentElement.id) {
            $(dropdown_item[i]).removeClass('active');
            }
        }
        $this.addClass('active');
        $this.context.parentElement.parentElement.firstElementChild.firstChild.data = $this.context.textContent;
        variable_property_id = $(this).data('key');
        value = $(this).data('value').toString();
        if (value == ""){
            add_notification('please provide a value',3);
        }else {
            $.ajax({
                type: 'post',
                url: ROOT_URL+'form/write_property/',
                data: {variable_property_id:variable_property_id, value:value},
                success: function (data) {

                },
                error: function(data) {
                    add_notification('write plug selected failed',3);
                }
            });
        }
    });
    reload_top10_ranking();
    $(window).on('hashchange', function() {
        // Check if we are on a page that need to show the TOP10QAs
        dropdown_TOP10QA = document.getElementsByClassName("dropdown-TOP10QA");
        pages = document.getElementsByClassName("sub-page");
        for (i=0;i<pages.length;i++){
            if (pages[i].id == window.location.hash.substr(1)) {
                if (pages[i].getElementsByClassName("ShowTOP10QA").length) {
                    questions = document.getElementsByClassName("dropdown-TOP10QA")[0].getElementsByClassName("input-group-addon-label");
                    input_group = document.getElementsByClassName("dropdown-TOP10QA")[0].getElementsByClassName("input-group");
                    //changes the number and value of the questions
                    $.ajax({
                        url: ROOT_URL+'json/query_top10_question/',
                        dataType: "json",
                        type: "POST",
                        data: {},
                        success: function (data) {
                            questions[0].textContent = data['question1'];
                            questions[1].textContent = data['question2'];
                            questions[2].textContent = data['question3'];
                            questions[3].textContent = data['question4'];
                            if ((questions[0].textContent != "Question1" && questions[0].textContent != "")
                            || (questions[1].textContent != "Question2" && questions[1].textContent != "")
                            || (questions[2].textContent != "Question3" && questions[2].textContent != "")
                            || (questions[3].textContent != "Question4" && questions[3].textContent != "")) {
                                $(".dropdown-TOP10QA").show();
                                for (i=0;i<questions.length;i++) {
                                    if (questions[i].textContent != "Question1" && questions[i].textContent != "") {
                                        input_group[i].classList.remove("hidden");

                                    }
                                    else {
                                        input_group[i].className += " hidden"
                                    }
                                }
                            }else {
                                $(".dropdown-TOP10QA").hide();
                            }
                        },
                        error: function(data) {
                            console.log("cache top10 question failed ");
                            console.log(data);
                            add_notification('cache top10 question failed',3);
                        }
                    });
                }else {
                    $(".dropdown-TOP10QA").hide();
                }
            }
        }
    });
});