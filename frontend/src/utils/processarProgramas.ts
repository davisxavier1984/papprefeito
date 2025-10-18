import type {
  DetalhamentoPrograma,
  ResumoPlanoOrcamentario,
  DadosPagamento,
  ComponenteValor,
  DetalhamentoSaudeBucal,
} from '../types';

/**
 * Processa os dados de financiamento e pagamentos para gerar
 * informações detalhadas de cada programa
 */
export function processarProgramas(
  resumos: ResumoPlanoOrcamentario[],
  pagamento?: DadosPagamento
): DetalhamentoPrograma[] {
  if (!resumos || resumos.length === 0) {
    return [];
  }

  const programas: DetalhamentoPrograma[] = [];

  // 1. eSF/eAP - Equipes de Saúde da Família
  const esfEapResumo = resumos.find((r) =>
    r.dsPlanoOrcamentario.includes('Equipes de Saúde da Família')
  );

  if (esfEapResumo) {
    const qtEsfCredenciado = pagamento?.qtEsfCredenciado || 0;
    const qtTetoEsf = pagamento?.qtTetoEsf || 0;
    const qtEapCredenciadas = pagamento?.qtEapCredenciadas || 0;
    const qtTetoEap = pagamento?.qtTetoEap || 0;

    const percentualEsf =
      qtTetoEsf > 0 ? Math.round((qtEsfCredenciado / qtTetoEsf) * 100) : 0;

    const temDesconto = (esfEapResumo.vlDesconto || 0) < 0;
    const percentualDesconto = esfEapResumo.vlIntegral
      ? Math.abs(((esfEapResumo.vlDesconto || 0) / esfEapResumo.vlIntegral) * 100)
      : 0;

    const oportunidadesEsf = qtTetoEsf - qtEsfCredenciado;
    const oportunidadesEap = qtTetoEap - qtEapCredenciadas;

    const alertas: string[] = [];
    const oportunidades: string[] = [];

    if (qtEsfCredenciado > qtTetoEsf) {
      alertas.push(`${qtEsfCredenciado - qtTetoEsf} equipes eSF acima do teto`);
    }

    if (oportunidadesEsf > 0) {
      oportunidades.push(`Pode credenciar mais ${oportunidadesEsf} equipes eSF`);
    }

    if (oportunidadesEap > 0) {
      oportunidades.push(`${oportunidadesEap} vagas eAP disponíveis`);
    }

    const componentesValor: ComponenteValor[] = [];
    if (pagamento?.vlFixoEsf) {
      componentesValor.push({ nome: 'Fixo eSF', valor: pagamento.vlFixoEsf });
    }
    if (pagamento?.vlVinculoEsf) {
      componentesValor.push({ nome: 'Vínculo eSF', valor: pagamento.vlVinculoEsf });
    }
    if (pagamento?.vlQualidadeEsf) {
      componentesValor.push({ nome: 'Qualidade eSF', valor: pagamento.vlQualidadeEsf });
    }

    programas.push({
      codigo: 'esf-eap',
      nome: 'Equipes de Saúde da Família',
      icone: '👥',
      cor: temDesconto ? '#f59e0b' : '#22c55e',
      quantidades: {
        credenciados: qtEsfCredenciado,
        homologados: pagamento?.qtEsfHomologado || 0,
        pagos: pagamento?.qtEsf100pcPgto || 0,
        teto: qtTetoEsf,
        percentual: percentualEsf,
        detalhes: `${qtEsfCredenciado} credenciadas / ${qtTetoEsf} teto (${percentualEsf}%)`,
      },
      quantidadesSecundarias: {
        credenciados: qtEapCredenciadas,
        teto: qtTetoEap,
        percentual: qtTetoEap > 0 ? Math.round((qtEapCredenciadas / qtTetoEap) * 100) : 0,
        detalhes: `eAP: ${qtEapCredenciadas} / ${qtTetoEap}`,
      },
      vlIntegral: esfEapResumo.vlIntegral,
      vlDesconto: esfEapResumo.vlDesconto,
      percentualDesconto: percentualDesconto,
      vlEfetivoRepasse: esfEapResumo.vlEfetivoRepasse,
      componentesValor: componentesValor.length > 0 ? componentesValor : undefined,
      status: temDesconto ? 'desconto' : alertas.length > 0 ? 'alerta' : 'ok',
      badge: temDesconto ? '⚠️ Desconto aplicado' : '✓ Ativo',
      alertas: alertas.length > 0 ? alertas : undefined,
      oportunidades: oportunidades.length > 0 ? oportunidades : undefined,
    });
  }

  // 2. Saúde Bucal - Dividido em cards separados
  const sbResumo = resumos.find((r) =>
    r.dsPlanoOrcamentario.includes('Saúde Bucal')
  );

  if (sbResumo) {
    // 2.1 ESB - Equipes de Saúde Bucal
    const qtSb40hCredenciada = pagamento?.qtSb40hCredenciada || 0;
    const qtSb40hDifCredenciada = pagamento?.qtSb40hDifCredenciada || 0;
    const qtTetoSb40h = pagamento?.qtTetoSb40h || 0;
    const qtTetoSbChDif = pagamento?.qtTetoSbChDif || 0;

    const percentual =
      qtTetoSb40h > 0 ? Math.round((qtSb40hCredenciada / qtTetoSb40h) * 100) : 0;

    const oportunidades: string[] = [];
    if (qtSb40hCredenciada < qtTetoSb40h) {
      const vagas = qtTetoSb40h - qtSb40hCredenciada;
      oportunidades.push(`Pode credenciar mais ${vagas} equipes 40h`);
    }
    if (qtTetoSbChDif > 0) {
      oportunidades.push(`${qtTetoSbChDif} vagas CH diferenciada disponíveis`);
    }

    const componentesValor: ComponenteValor[] = [];
    if (pagamento?.vlPagamentoEsb40h) {
      componentesValor.push({ nome: 'ESB 40h', valor: pagamento.vlPagamentoEsb40h });
    }
    if (pagamento?.vlPagamentoEsb40hQualidade) {
      componentesValor.push({
        nome: 'Qualidade',
        valor: pagamento.vlPagamentoEsb40hQualidade,
      });
    }
    if (pagamento?.vlPagamentoEsbChDiferenciada) {
      componentesValor.push({
        nome: 'CH Diferenciada',
        valor: pagamento.vlPagamentoEsbChDiferenciada,
      });
    }
    if (pagamento?.vlPagamentoImplantacaoEsb40h) {
      componentesValor.push({
        nome: 'Implantação',
        valor: pagamento.vlPagamentoImplantacaoEsb40h,
      });
    }

    const vlTotalEsb =
      (pagamento?.vlPagamentoEsb40h || 0) +
      (pagamento?.vlPagamentoEsb40hQualidade || 0) +
      (pagamento?.vlPagamentoEsbChDiferenciada || 0) +
      (pagamento?.vlPagamentoImplantacaoEsb40h || 0);

    programas.push({
      codigo: 'esb',
      nome: 'ESB - Equipes de Saúde Bucal',
      icone: '🦷',
      cor: percentual === 100 ? '#22c55e' : '#0ea5e9',
      quantidades: {
        credenciados: qtSb40hCredenciada,
        homologados: pagamento?.qtSb40hHomologado || 0,
        pagos:
          (pagamento?.qtSbPagamentoModalidadeI || 0) +
          (pagamento?.qtSbPagamentoModalidadeII || 0),
        teto: qtTetoSb40h,
        percentual: percentual,
        detalhes: `${qtSb40hCredenciada} / ${qtTetoSb40h} teto (${percentual}%)`,
      },
      quantidadesSecundarias:
        qtTetoSbChDif > 0
          ? {
              credenciados: qtSb40hDifCredenciada,
              teto: qtTetoSbChDif,
              detalhes: `CH Diferenciada: ${qtSb40hDifCredenciada} / ${qtTetoSbChDif}`,
            }
          : undefined,
      vlEfetivoRepasse: vlTotalEsb,
      componentesValor: componentesValor.length > 0 ? componentesValor : undefined,
      status: percentual === 100 ? 'ok' : 'oportunidade',
      badge: percentual === 100 ? '✓ 100% recebido' : '💡 Oportunidade',
      oportunidades: oportunidades.length > 0 ? oportunidades : undefined,
    });

    // 2.2 CEO - Centro de Especialidades Odontológicas
    const vlCeoMunicipal = pagamento?.vlPagamentoCeoMunicipal || 0;
    const vlCeoEstadual = pagamento?.vlPagamentoCeoEstadual || 0;
    const vlTotalCeo = vlCeoMunicipal + vlCeoEstadual;

    if (vlTotalCeo > 0) {
      const componentesValorCeo: ComponenteValor[] = [];
      if (vlCeoMunicipal > 0) {
        componentesValorCeo.push({ nome: 'CEO Municipal', valor: vlCeoMunicipal });
      }
      if (vlCeoEstadual > 0) {
        componentesValorCeo.push({ nome: 'CEO Estadual', valor: vlCeoEstadual });
      }

      programas.push({
        codigo: 'ceo',
        nome: 'CEO - Centro de Especialidades Odontológicas',
        icone: '🏥',
        cor: '#8b5cf6',
        quantidades: {
          detalhes:
            vlCeoMunicipal > 0 && vlCeoEstadual > 0
              ? 'CEO Municipal e Estadual'
              : vlCeoMunicipal > 0
              ? 'CEO Municipal'
              : 'CEO Estadual',
        },
        vlEfetivoRepasse: vlTotalCeo,
        componentesValor: componentesValorCeo,
        status: 'ok',
        badge: '✓ Ativo',
      });
    }

    // 2.3 SESB - Serviço de Especialidades em Saúde Bucal (municípios até 20mil hab)
    const vlPagamentoSesb = pagamento?.vlPagamentoSesb || 0;
    const vlDesempenhoSesb = pagamento?.vlPagamentoDesempenhoSesb || 0;
    const vlTotalSesb = pagamento?.vlTotalPagamentoSesb || vlPagamentoSesb + vlDesempenhoSesb;

    if (vlTotalSesb > 0) {
      const componentesValorSesb: ComponenteValor[] = [];
      if (vlPagamentoSesb > 0) {
        componentesValorSesb.push({ nome: 'Pagamento', valor: vlPagamentoSesb });
      }
      if (vlDesempenhoSesb > 0) {
        componentesValorSesb.push({ nome: 'Desempenho', valor: vlDesempenhoSesb });
      }

      programas.push({
        codigo: 'sesb',
        nome: 'SESB - Serviço de Especialidades em Saúde Bucal',
        icone: '🏥',
        cor: '#06b6d4',
        quantidades: {
          detalhes: 'Municípios elegíveis (até 20 mil habitantes)',
        },
        vlEfetivoRepasse: vlTotalSesb,
        componentesValor: componentesValorSesb.length > 0 ? componentesValorSesb : undefined,
        status: 'ok',
        badge: '✓ Ativo',
      });
    }

    // 2.4 LRPD - Laboratório Regional de Prótese Dentária
    const vlLrpdMunicipal = pagamento?.vlPagamentoLrpdMunicipal || 0;
    const vlLrpdEstadual = pagamento?.vlPagamentoLrpdEstadual || 0;
    const vlTotalLrpd = vlLrpdMunicipal + vlLrpdEstadual;

    if (vlTotalLrpd > 0) {
      const componentesValorLrpd: ComponenteValor[] = [];
      if (vlLrpdMunicipal > 0) {
        componentesValorLrpd.push({ nome: 'LRPD Municipal', valor: vlLrpdMunicipal });
      }
      if (vlLrpdEstadual > 0) {
        componentesValorLrpd.push({ nome: 'LRPD Estadual', valor: vlLrpdEstadual });
      }

      programas.push({
        codigo: 'lrpd',
        nome: 'LRPD - Laboratório Regional de Prótese Dentária',
        icone: '🔬',
        cor: '#ec4899',
        quantidades: {
          detalhes:
            vlLrpdMunicipal > 0 && vlLrpdEstadual > 0
              ? 'LRPD Municipal e Estadual'
              : vlLrpdMunicipal > 0
              ? 'LRPD Municipal'
              : 'LRPD Estadual',
        },
        vlEfetivoRepasse: vlTotalLrpd,
        componentesValor: componentesValorLrpd,
        status: 'ok',
        badge: '✓ Ativo',
      });
    }
  }

  // 3. eMulti - Equipes Multiprofissionais
  const emultiResumo = resumos.find((r) =>
    r.dsPlanoOrcamentario.includes('Multiprofissionais')
  );

  if (emultiResumo) {
    const qtEmultiCredenciadas = pagamento?.qtEmultiCredenciadas || 0;
    const qtTetoComplementar = pagamento?.qtTetoEmultiComplementar || 0;
    const qtTetoEstrategica = pagamento?.qtTetoEmultiEstrategica || 0;
    const qtPagamentoEstrategica = pagamento?.qtEmultiPagamentoEstrategica || 0;
    const qtAtendRemoto = pagamento?.qtEmultiPagasAtendRemoto || 0;

    const percentual =
      qtTetoComplementar > 0
        ? Math.round((qtEmultiCredenciadas / qtTetoComplementar) * 100)
        : 0;

    const oportunidadeEstrategica = qtTetoEstrategica - qtPagamentoEstrategica;

    const oportunidades: string[] = [];
    if (oportunidadeEstrategica > 0) {
      oportunidades.push(`${oportunidadeEstrategica} equipes estratégicas disponíveis`);
    }

    const componentesValor: ComponenteValor[] = [];
    if (pagamento?.vlPagamentoEmultiCusteio) {
      componentesValor.push({ nome: 'Custeio', valor: pagamento.vlPagamentoEmultiCusteio });
    }
    if (pagamento?.vlPagamentoEmultiQualidade) {
      componentesValor.push({
        nome: 'Qualidade',
        valor: pagamento.vlPagamentoEmultiQualidade,
      });
    }
    if (pagamento?.vlPagamentoEmultiAtendimentoRemoto) {
      componentesValor.push({
        nome: 'Atend. Remoto',
        valor: pagamento.vlPagamentoEmultiAtendimentoRemoto,
      });
    }

    const detalhesSecundarios = qtAtendRemoto > 0
      ? ` (${qtAtendRemoto} com atend. remoto)`
      : '';

    programas.push({
      codigo: 'emulti',
      nome: 'Equipes Multiprofissionais',
      icone: '🏥',
      cor: '#22c55e',
      quantidades: {
        credenciados: qtEmultiCredenciadas,
        homologados: pagamento?.qtEmultiHomologado || 0,
        pagos: pagamento?.qtEmultiPagas || 0,
        teto: qtTetoComplementar,
        percentual: percentual,
        detalhes: `${qtEmultiCredenciadas} / ${qtTetoComplementar} (Complementar)${detalhesSecundarios}`,
      },
      quantidadesSecundarias: qtTetoEstrategica > 0 ? {
        credenciados: qtPagamentoEstrategica,
        teto: qtTetoEstrategica,
        percentual: Math.round((qtPagamentoEstrategica / qtTetoEstrategica) * 100),
        detalhes: `Estratégica: ${qtPagamentoEstrategica} / ${qtTetoEstrategica}`,
      } : undefined,
      vlEfetivoRepasse: emultiResumo.vlEfetivoRepasse,
      componentesValor: componentesValor.length > 0 ? componentesValor : undefined,
      status: 'ok',
      badge: '✓ Ativo',
      oportunidades: oportunidades.length > 0 ? oportunidades : undefined,
    });
  }

  // 4. ACS - Agentes Comunitários de Saúde
  const acsResumo = resumos.find((r) =>
    r.dsPlanoOrcamentario.includes('Agentes Comunitários')
  );

  if (acsResumo) {
    const qtAcsDiretoCredenciado = pagamento?.qtAcsDiretoCredenciado || 0;
    const qtAcsDiretoPgto = pagamento?.qtAcsDiretoPgto || 0;
    const qtTetoAcs = pagamento?.qtTetoAcs || 0;

    const percentual =
      qtTetoAcs > 0 ? Math.round((qtAcsDiretoCredenciado / qtTetoAcs) * 100) : 0;

    const acimaDoTeto = qtAcsDiretoCredenciado > qtTetoAcs;
    const semPagamento = qtAcsDiretoCredenciado - qtAcsDiretoPgto;
    const vagasDisponiveis = qtTetoAcs - qtAcsDiretoCredenciado;

    const alertas: string[] = [];
    const oportunidades: string[] = [];

    if (acimaDoTeto) {
      alertas.push(`⚠️ ${qtAcsDiretoCredenciado - qtTetoAcs} agentes acima do teto`);
    }

    if (semPagamento > 0) {
      alertas.push(`${semPagamento} agentes credenciados sem pagamento`);
    }

    if (!acimaDoTeto && vagasDisponiveis > 0) {
      oportunidades.push(`Pode credenciar mais ${vagasDisponiveis} agentes`);
    }

    programas.push({
      codigo: 'acs',
      nome: 'Agentes Comunitários de Saúde',
      icone: '🚶',
      cor: acimaDoTeto ? '#ef4444' : '#22c55e',
      quantidades: {
        credenciados: qtAcsDiretoCredenciado,
        pagos: qtAcsDiretoPgto,
        teto: qtTetoAcs,
        percentual: percentual,
        detalhes: `${qtAcsDiretoCredenciado} credenciados / ${qtAcsDiretoPgto} pagos / ${qtTetoAcs} teto`,
      },
      vlEfetivoRepasse: acsResumo.vlEfetivoRepasse,
      status: acimaDoTeto ? 'alerta' : 'ok',
      badge: acimaDoTeto ? '⚠️ Acima do teto' : '✓ Ativo',
      alertas: alertas.length > 0 ? alertas : undefined,
      oportunidades: oportunidades.length > 0 ? oportunidades : undefined,
    });
  }

  // 5. Demais Programas
  const demaisResumo = resumos.find((r) =>
    r.dsPlanoOrcamentario.includes('Demais programas')
  );

  if (demaisResumo) {
    const servicosCredenciados: string[] = [];

    if (pagamento?.qtIafCredenciado && pagamento.qtIafCredenciado > 0) {
      servicosCredenciados.push(
        `IAF: ${pagamento.qtIafCredenciado} credenciado${pagamento.qtIafCredenciado > 1 ? 's' : ''}`
      );
    }

    if (pagamento?.qtUomCredenciada && pagamento.qtUomCredenciada > 0) {
      servicosCredenciados.push(`UOM: ${pagamento.qtUomCredenciada}`);
    }

    if (pagamento?.qtAcademiaSaudeCredenciado && pagamento.qtAcademiaSaudeCredenciado > 0) {
      servicosCredenciados.push(`Academia Saúde: ${pagamento.qtAcademiaSaudeCredenciado}`);
    }

    const isInativo = demaisResumo.vlEfetivoRepasse === 0;

    programas.push({
      codigo: 'demais',
      nome: 'Demais Programas',
      icone: '⚙️',
      cor: isInativo ? '#64748b' : '#22c55e',
      quantidades: servicosCredenciados.length > 0 ? {
        detalhes: servicosCredenciados.join(' | '),
      } : {
        detalhes: '0 credenciados',
      },
      vlEfetivoRepasse: demaisResumo.vlEfetivoRepasse,
      status: isInativo ? 'inativo' : 'ok',
      badge: isInativo ? '❌ Sem credenciamento' : '✓ Ativo',
    });
  }

  // 6. Per Capita
  const perCapitaResumo = resumos.find((r) =>
    r.dsPlanoOrcamentario.includes('per capita')
  );

  if (perCapitaResumo) {
    const qtPopulacao = pagamento?.qtPopulacao || 0;
    const perCapitaMensal =
      qtPopulacao > 0 ? perCapitaResumo.vlEfetivoRepasse / qtPopulacao : 0;

    programas.push({
      codigo: 'percapita',
      nome: 'Componente per capita',
      icone: '👨‍👩‍👧‍👦',
      cor: '#0ea5e9',
      populacao: qtPopulacao,
      anoReferencia: pagamento?.nuAnoRefPopulacaoIbge,
      perCapitaMensal: perCapitaMensal,
      quantidades: {
        detalhes: `População: ${qtPopulacao.toLocaleString('pt-BR')} habitantes`,
      },
      vlEfetivoRepasse: perCapitaResumo.vlEfetivoRepasse,
      status: 'ok',
      badge: '✓ Ativo',
    });
  }

  return programas;
}

/**
 * Processa dados detalhados de Saúde Bucal
 */
export function processarSaudeBucalDetalhado(
  pagamento?: DadosPagamento
): DetalhamentoSaudeBucal | undefined {
  if (!pagamento) {
    return undefined;
  }

  // ESB - Equipes de Saúde Bucal
  const esb = {
    modalidade40h: {
      credenciadas: pagamento.qtSb40hCredenciada || 0,
      homologadas: pagamento.qtSb40hHomologado || 0,
      modalidadeI: pagamento.qtSbPagamentoModalidadeI || 0,
      modalidadeII: pagamento.qtSbPagamentoModalidadeII || 0,
    },
    chDiferenciada: {
      credenciadas: pagamento.qtSb40hDifCredenciada || 0,
      homologadas: pagamento.qtSbChDifHomologado || 0,
      modalidade20h: pagamento.qtSbPagamentoDifModalidade20Horas || 0,
      modalidade30h: pagamento.qtSbPagamentoDifModalidade30Horas || 0,
    },
    quilombolasAssentamentos: {
      modalidadeI: pagamento.qtSbEqpQuilombAssentModalI || 0,
      modalidadeII: pagamento.qtSbEqpQuilombAssentModalII || 0,
    },
    implantacao: pagamento.qtSbEquipeImplantacao || 0,
    valores: {
      pagamento: pagamento.vlPagamentoEsb40h || 0,
      qualidade: pagamento.vlPagamentoEsb40hQualidade || 0,
      chDiferenciada: pagamento.vlPagamentoEsbChDiferenciada || 0,
      implantacao: pagamento.vlPagamentoImplantacaoEsb40h || 0,
    },
  };

  // UOM - Unidade Odontológica Móvel
  const uom = {
    credenciadas: pagamento.qtUomCredenciada || 0,
    homologadas: pagamento.qtUomHomologado || 0,
    pagas: pagamento.qtUomPgto || 0,
    valores: {
      pagamento: pagamento.vlPagamentoUom || 0,
      implantacao: pagamento.vlPagamentoUomImplantacao || 0,
    },
  };

  // CEO - Centro de Especialidades Odontológicas
  const ceo = {
    municipal: pagamento.vlPagamentoCeoMunicipal || 0,
    estadual: pagamento.vlPagamentoCeoEstadual || 0,
  };

  // LRPD - Laboratório Regional de Prótese Dentária
  const lrpd = {
    municipal: pagamento.vlPagamentoLrpdMunicipal || 0,
    estadual: pagamento.vlPagamentoLrpdEstadual || 0,
  };

  // Calcular totais
  const vlTotal =
    esb.valores.pagamento +
    esb.valores.qualidade +
    esb.valores.chDiferenciada +
    esb.valores.implantacao +
    uom.valores.pagamento +
    uom.valores.implantacao +
    ceo.municipal +
    ceo.estadual +
    lrpd.municipal +
    lrpd.estadual;

  const qtTotalEquipes =
    esb.modalidade40h.credenciadas +
    esb.chDiferenciada.credenciadas +
    esb.quilombolasAssentamentos.modalidadeI +
    esb.quilombolasAssentamentos.modalidadeII +
    uom.credenciadas;

  const totais = {
    vlTotal,
    qtTotalEquipes,
  };

  return {
    esb,
    uom,
    ceo,
    lrpd,
    totais,
  };
}
