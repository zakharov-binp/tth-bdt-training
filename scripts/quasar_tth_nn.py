import os
from tthAnalysis.bdtHyperparameterOptimization import universal
from tthAnalysis.bdtTraining import xgb_tth as ttHxt
from tthAnalysis.bdtHyperparameterOptimization import nn_tools as nnt
from tthAnalysis.bdtHyperparameterOptimization import pso_main as pm


def main():
    global_settings = universal.read_settings('global')
    channel = global_settings['channel']
    bdtType = global_settings['bdtType']
    trainvar = global_settings['trainvar']
    pso_settings = universal.read_settings('pso')
    fnFile = '_'.join(['fn', channel])
    importString = "".join(['tthAnalysis.bdtTraining.', fnFile])
    cf = __import__(importString, fromlist=[''])
    nthread = global_settings['nthread']
    output_dir = os.path.expandvars(global_settings['output_dir'])
    cmssw_base_path = os.path.expandvars('$CMSSW_BASE')
    main_dir = os.path.join(
        cmssw_base_path,
        'src',
        'tthAnalysis',
        'bdtHyperparameterOptimization'
    )
    param_file = os.path.join(
        main_dir,
        'data',
        'nn_parameters.json'
    )
    value_dicts = universal.read_parameters(param_file)
    nn_hyperparameters = nnt.prepare_run_params(
        value_dicts, pso_settings['sample_size'])
    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)
    data, trainvars = ttHxt.tth_analysis_main(
        channel, bdtType, nthread,
        output_dir, trainvar, cf
    )
    data_dict = nnt.create_data_dict(data, trainvars)
    pso_settings = pm.read_weights()

    print("\n============ Starting hyperparameter optimization ==========\n")
    result_dict = pm.run_pso(
        data_dict, value_dicts, nnt.ensemble_fitness, parameter_dicts
    )
    print("\n============ Saving results ================\n")
    universal.save_results(result_dict, output_dir, plot_extras=True)
    sm.clear_from_files(global_settings)
    print("Results saved to " + str(output_dir))


if __name__ == '__main__':
    main()